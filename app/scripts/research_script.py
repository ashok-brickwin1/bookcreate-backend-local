import os
import sys
import time
import json
import logging
import requests
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APITimeoutError, APIConnectionError, APIStatusError
from perplexity import Perplexity
import concurrent.futures
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

# ==========================
# 1) Load Environment & Config
# ==========================
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()  # Summaries
XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()  # Grok
ENRICH_SO_API_KEY = os.getenv("ENRICH_SO_API_KEY", "").strip()  # Enrich.so data enrichment

GROK_ENDPOINT_BASE = "https://api.x.ai/v1"
ENRICH_SO_ENDPOINT = "https://api.enrich.so/v1/api/person"

# Filenames
INPUT_CSV_PATH = "input_people.csv"
OUTPUT_DATA_DIR = "output_data"
BIOS_DIR = "bios"
LOG_FILE_PATH = "research_log.log"

# Models
DEFAULT_PERPLEXITY_MODEL = "sonar-pro" # Ensure this matches your API access
DEFAULT_GROK_MODEL = "grok-4-latest"   # Ensure this matches your API access

# --- Concurrency & Retry Settings ---
MAX_WORKERS = 5  # Set based on the lowest API concurrency limit (iScraper = 5)
RETRY_ATTEMPTS = 3 # Number of retry attempts for API calls
RETRY_WAIT_MIN_SECONDS = 1 # Minimum wait time for retries
RETRY_WAIT_MAX_SECONDS = 10 # Maximum wait time for retries

# Delays (Keep only essential ones)
CHUNK_SUMMARY_DELAY = 1.0 # Delay between summarizing chunks for the *same* person (helps Perplexity RPM)

# API Timeouts (seconds)
GROK_TIMEOUT = 120

# ==========================
# 2) Logging Setup
# ==========================
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - Thread-%(thread)d - %(message)s')

file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

# Clear existing handlers and set up basic config
logging.getLogger().handlers = []
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logging.getLogger("requests").setLevel(logging.WARNING) # Quieten requests library logs
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Quieten urllib3 logs

# ==========================
# 3) HTTP Sessions & API Clients
# ==========================
# Perplexity client - SDK reads from PERPLEXITY_API_KEY env var automatically
perplexity_client = None
if PERPLEXITY_API_KEY:
    try:
        # Set env var for SDK to pick up (SDK reads from environment)
        os.environ['PERPLEXITY_API_KEY'] = PERPLEXITY_API_KEY
        perplexity_client = Perplexity()
    except Exception as e:
        logging.error(f"Failed to initialize Perplexity client: {e}")
        perplexity_client = None
else:
    logging.warning("PERPLEXITY_API_KEY not set - research summarization will be skipped")

# Grok client (initialized later if needed, or globally if API key guaranteed)
grok_client = None
if XAI_API_KEY:
    try:
        grok_client = OpenAI(api_key=XAI_API_KEY, base_url=GROK_ENDPOINT_BASE)
    except Exception as e:
        logging.error(f"Failed to initialize Grok client: {e}")
        grok_client = None # Ensure it's None if init fails

# ==========================
# 4) Helper Functions (Mostly Unchanged)
# ==========================
def safe_get(d, key, default=''):
    if not isinstance(d, dict):
        return default
    val = d.get(key)
    if pd.isna(val):
        return default
    return str(val) if val is not None else default

def sanitize_filename(name: str) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()
    if not safe:
        safe = "unnamed"
    return safe.replace(" ", "_")

def chunk_text(text, chunk_size=3000):
    # Simple chunking, consider more sophisticated methods if needed (e.g., sentence boundaries)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def parse_linkedin_slug(link_url: str):
    if not link_url: return None
    lower = link_url.lower()
    if "linkedin.com/in/" in lower:
        slug = lower.split("linkedin.com/in/")[-1].split("/")[0].split("?")[0]
        return slug
    return None

# ==========================
# 5) API Call Functions with Retries
# ==========================

# Define exceptions to retry on for Requests
requests_retry_exceptions = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.HTTPError # Will add condition below
)
# Define specific HTTP status codes to retry on for Requests
http_retry_status_codes = {429, 500, 502, 503, 504}

def should_retry_requests_exception(exception):
    """Check if a Requests exception should be retried."""
    if isinstance(exception, requests.exceptions.HTTPError):
        # Retry only on specific server-side/rate-limit errors
        return exception.response.status_code in http_retry_status_codes
    # Retry on Timeout and ConnectionError
    return isinstance(exception, requests_retry_exceptions)

# Define exceptions to retry on for OpenAI client
openai_retry_exceptions = (
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    APIStatusError # Will add condition below
)

def should_retry_openai_exception(exception):
    """Check if an OpenAI exception should be retried."""
    if isinstance(exception, APIStatusError):
        # Retry only on specific server-side/rate-limit errors
        # Adjust status codes as needed based on Grok's API behavior
        return exception.status_code in {429, 500, 502, 503, 504}
    # Retry on Timeout, ConnectionError, and explicit RateLimitError
    return isinstance(exception, openai_retry_exceptions)


def call_perplexity_for_summary(text_to_summarize, context_title="Large Data"):
    global perplexity_client
    if not PERPLEXITY_API_KEY:
        return "Error: Missing Perplexity API key"
    if not perplexity_client:
        return "Error: Perplexity client not initialized"

    system_msg = "You are an assistant that summarizes JSON or text data succinctly, focusing on key professional information."
    user_msg = (
        f"Summarize the key professional details from the following data ({context_title}). "
        f"Extract only factual information present in the text. Avoid conversational filler.\n\n"
        f"Data:\n```json\n{text_to_summarize}\n```" # Assume JSON or treat as text
    )

    try:
        completion = perplexity_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            model=DEFAULT_PERPLEXITY_MODEL,
            temperature=0.1, # Low temp for factual summary
            max_tokens=1024 # Adjust as needed, shorter for summaries
        )
        
        summary = completion.choices[0].message.content.strip()
        if summary:
            return summary
        else:
            logging.warning(f"[Perplexity] Empty summary received for '{context_title}'")
            return f"Error: Perplexity returned empty summary for '{context_title}'"
    except Exception as e:
        logging.error(f"[Perplexity] Unexpected error during summary for '{context_title}': {e}")
        return f"Error summarizing '{context_title}': {str(e)}"


def summarize_large_field(field_data, context_title="Large Field"):
    """Summarizes large data, chunking if necessary."""
    if not field_data:
        return f"No data provided for '{context_title}'."

    try:
        # Attempt to serialize dicts/lists, otherwise treat as string
        if isinstance(field_data, (dict, list)):
            text_str = json.dumps(field_data, indent=2, ensure_ascii=False)
        else:
            text_str = str(field_data)
    except Exception as e:
        logging.error(f"Error converting field data to string for '{context_title}': {e}")
        return f"Error processing data for '{context_title}'"

    # Check size *before* making the first call
    # Use a slightly smaller threshold than chunk_size to avoid single tiny chunk overhead
    CHUNK_THRESHOLD = 2800
    CHUNK_SIZE = 3000

    if len(text_str) < CHUNK_THRESHOLD:
        logging.info(f"Summarizing '{context_title}' (size: {len(text_str)}) directly.")
        return call_perplexity_for_summary(text_str, context_title)
    else:
        logging.info(f"Field '{context_title}' is large ({len(text_str)} chars). Chunking required.")
        parts = chunk_text(text_str, CHUNK_SIZE)
        partial_summaries = []
        for i, chunk in enumerate(parts):
            chunk_title = f"{context_title} (chunk {i+1}/{len(parts)})"
            logging.info(f"Summarizing {chunk_title}")
            summary = call_perplexity_for_summary(chunk, chunk_title)
            if summary.startswith("Error"):
                 logging.warning(f"Failed to summarize {chunk_title}. Stopping summary for this field.")
                 # Decide: return partial summary, or error? Returning error is safer.
                 return f"Error summarizing chunk {i+1} for '{context_title}'."

            partial_summaries.append(f"--- Summary of Chunk {i+1} ---\n{summary}")
            if i < len(parts) - 1:
                time.sleep(CHUNK_SUMMARY_DELAY) # Delay between chunk calls

        combined_text = "\n\n".join(partial_summaries)
        logging.info(f"Combining {len(parts)} partial summaries for '{context_title}'.")

        # Final summary of summaries
        final_summary = call_perplexity_for_summary(combined_text, f"{context_title} - Combined Summary")
        return final_summary


def read_research_files(person_name: str):
    """Read local research files for a person and return combined text and file list."""
    candidates = [
        os.path.join("research", person_name),
        os.path.join("research", person_name.replace(" ", "_"))
    ]
    for base in candidates:
        if os.path.isdir(base):
            break
    else:
        return "", []

    texts = []
    files = []
    try:
        for fname in sorted(os.listdir(base)):
            if not (fname.endswith(".md") or fname.endswith(".txt")):
                continue
            fpath = os.path.join(base, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    texts.append(f"# {fname}\n\n{content}")
                    files.append(fpath)
            except Exception as e:
                logging.warning(f"Failed reading research file {fpath}: {e}")
    except Exception as e:
        logging.warning(f"Error listing research dir {base}: {e}")

    return ("\n\n---\n\n".join(texts)).strip(), files


def condense_research_context(person_name: str):
    """Create a summary of local research files for a person, using Perplexity when available.
    Returns: (summary, files, raw_content)"""
    combined_text, files = read_research_files(person_name)
    if not combined_text:
        return "No external research context available.", files, ""

    if not PERPLEXITY_API_KEY:
        # Fallback: truncate raw text
        MAX_LEN = 2000
        truncated = (combined_text[:MAX_LEN] + "\n\n[Truncated]") if len(combined_text) > MAX_LEN else combined_text
        return truncated, files, combined_text

    summary = summarize_large_field(combined_text, f"Local Research Files for {person_name}")
    return summary, files, combined_text


def enrich_with_enrichso(email=None, linkedin_url=None):
    """Enrich data using Enrich.so API. Requires either email or LinkedIn URL.
    Returns: dict with enriched data or None if enrichment fails/not available."""
    if not ENRICH_SO_API_KEY:
        return None
    
    # Enrich.so primarily works with email addresses
    if not email and linkedin_url:
        # If we only have LinkedIn, we can't use Enrich.so (it requires email)
        logging.info("Enrich.so requires email address; LinkedIn URL alone not sufficient")
        return None
    
    if not email:
        return None
    
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {ENRICH_SO_API_KEY}'
    }
    payload = {'email': email}
    
    try:
        resp = requests.get(ENRICH_SO_ENDPOINT, params=payload, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            
            enriched_data = {
                "email": email,
                "full_name": result.get("displayName"),
                "first_name": result.get("firstName"),
                "last_name": result.get("lastName"),
                "linkedin": result.get("linkedInUrl"),
                "company": result.get("company", {}).get("name"),
                "company_website": result.get("company", {}).get("website"),
                "company_industry": result.get("company", {}).get("industry"),
                "company_size": result.get("company", {}).get("staff_count"),
                "job_title": result.get("jobTitle"),
                "location": result.get("location"),
                "twitter": result.get("social", {}).get("twitter"),
                "facebook": result.get("social", {}).get("facebook"),
                "github": result.get("social", {}).get("github"),
                "phone": result.get("phone"),
                "additional_emails": ", ".join(result.get("emails", [])) if result.get("emails") else None,
                "skills": ", ".join(result.get("skills", [])) if result.get("skills") else None,
                "education": ", ".join([edu.get("name", "") for edu in result.get("education", [])]) if result.get("education") else None,
                "experience": ", ".join([exp.get("title", "") + " at " + exp.get("company", "") for exp in result.get("experience", [])]) if result.get("experience") else None,
                "success": True
            }
            logging.info(f"Successfully enriched data for {email} via Enrich.so")
            return enriched_data
        else:
            logging.warning(f"Enrich.so API returned status {resp.status_code} for {email}")
            return None
    except requests.exceptions.RequestException as e:
        logging.warning(f"Enrich.so API request failed for {email}: {e}")
        return None
    except Exception as e:
        logging.warning(f"Unexpected error enriching {email}: {e}")
        return None


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_random_exponential(multiplier=1, min=RETRY_WAIT_MIN_SECONDS, max=RETRY_WAIT_MAX_SECONDS),
    retry=should_retry_openai_exception, # CORRECTED LINE
    reraise=True
)
def generate_final_bio_grok(csv_data, supplemental_context, enriched_data=None):
    """Generates the final biography using Grok, combining CSV, optional summarized research context, and enriched data."""
    global grok_client # Use the globally initialized client
    if not XAI_API_KEY: return "Error: Missing Grok API key"
    if not grok_client: return "Error: Grok client not initialized"

    first_name = safe_get(csv_data, "first_name", "the individual")

    # Build context string carefully
    context_lines = []
    context_lines.append("=== Source: CSV Data ===")
    for k, v in csv_data.items():
        if v and k not in ["full_name", "linkedin"]: # Avoid redundancy if possible
            context_lines.append(f"- {k.replace('_', ' ').title()}: {v}")

    # Add enriched data if available
    if enriched_data and enriched_data.get("success"):
        context_lines.append("\n=== Source: Enrich.so Data (enriched) ===")
        for k, v in enriched_data.items():
            if v and k not in ["success", "email"]:  # Skip metadata fields
                context_lines.append(f"- {k.replace('_', ' ').title()}: {v}")

    context_lines.append("\n=== Source: Local Research Summary (optional) ===")
    context_lines.append(supplemental_context if supplemental_context else "No external research context available.")

    full_context = "\n".join(context_lines)

    # Simple truncation if context is massive (Grok has large limits, but good practice)
    MAX_CONTEXT_LEN = 25000 # Adjust based on Grok model limits if known
    if len(full_context) > MAX_CONTEXT_LEN:
        logging.warning(f"Context length ({len(full_context)}) > {MAX_CONTEXT_LEN}. Truncating.")
        full_context = full_context[:MAX_CONTEXT_LEN] + "\n\n[Context Truncated...]"

    system_prompt = "You are a skilled professional writer creating concise, factual, and engaging third-person biographies based *only* on the provided source text. Do not invent information or use excessive praise."
    user_prompt = f"""
Based *strictly* on the information within the 'SOURCE TEXT' below, write a professional biography for {first_name}.

**Guidelines:**
- The biography should be a narrative, not just bullet points.
- Focus on professional experience, skills, education, and current role mentioned in the text.
- Start directly with the biography; avoid introductory phrases like "Here is the biography".
- Do *not* include any information not explicitly present in the 'SOURCE TEXT'. No assumptions or fabrications.
- Maintain a neutral, factual, and professional tone. Avoid overly enthusiastic or superlative language.
- Use clear and concise language. Vary sentence structure.
- If location/country is mentioned, incorporate it naturally. Use US English spelling unless localized spelling is clearly indicated in the source text.
- Aim for well-structured paragraphs, as many as needed, to give as complete a biography as possible with all the information you have without repetition or embelleshment.

**SOURCE TEXT:**
---
{full_context}
---

**Biography:**
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        completion = grok_client.chat.completions.create(
            model=DEFAULT_GROK_MODEL,
            messages=messages,
            temperature=0.2, # Lower temperature for more factual output
            max_tokens=1500 # Adjust based on desired bio length
            # Consider adding 'stop' sequences if needed
        )
        bio = completion.choices[0].message.content.strip()
        if bio:
            return bio
        else:
            logging.error("[Grok] Received empty biography response.")
            return "Error: Grok returned an empty biography."

    # Catch specific OpenAI errors first if needed, then general Exception
    except (APITimeoutError, APIConnectionError, RateLimitError, APIStatusError) as e:
         # These are handled by tenacity's retry, this block catches final failure
         logging.error(f"[Grok] API error for {first_name} after retries: {e}")
         return f"Error generating biography via Grok (API Error): {e}"
    except Exception as e:
        # Catch any other unexpected errors during the Grok call
        logging.exception(f"[Grok] Unexpected error generating bio for {first_name}: {e}") # Use logging.exception to include traceback
        return f"Error generating biography via Grok (Unexpected): {e}"


# ==========================
# 6) Main Processing Function for One Row
# ==========================
def process_row(row_data, index, total_rows):
    """Processes a single row: iScraper -> Summarize -> Grok Bio -> Save."""
    person_name = safe_get(row_data, 'full_name', f"Row_{index+1}")
    logging.info(f"--- Starting processing for {index+1}/{total_rows}: {person_name} ---")
    row_start_time = time.time()

    # --- Step A: Summarize Local Research Files (optional) ---
    research_start = time.time()
    research_summary, research_files, raw_research_content = condense_research_context(person_name)
    research_end = time.time()
    logging.info(f"Research context preparation took {research_end - research_start:.2f}s for {person_name}")

    # --- Step B: Enrich with Enrich.so (optional) ---
    enriched_data = None
    email = safe_get(row_data, "email")
    linkedin_url = safe_get(row_data, "linkedin")
    if email or linkedin_url:
        enrich_start = time.time()
        enriched_data = enrich_with_enrichso(email=email, linkedin_url=linkedin_url)
        enrich_end = time.time()
        if enriched_data:
            logging.info(f"Enrich.so enrichment took {enrich_end - enrich_start:.2f}s for {person_name}")
        else:
            logging.info(f"Enrich.so enrichment skipped or failed for {person_name}")

    # --- Step C: Generate Final Biography (Grok) ---
    final_bio_text = "Error: Bio generation skipped due to previous errors or missing key."
    grok_start = time.time()
    if XAI_API_KEY and grok_client: # Only proceed if Grok is configured
        final_bio_text = generate_final_bio_grok(row_data, research_summary, enriched_data)
    elif not XAI_API_KEY:
        logging.warning("Grok API key not found, skipping final biography generation.")
        final_bio_text = "Error: Grok API key not configured."
    else: # Client init failed
        logging.warning("Grok client not initialized, skipping final biography generation.")
        final_bio_text = "Error: Grok client initialization failed."

    grok_end = time.time()
    logging.info(f"Grok biography generation took {grok_end - grok_start:.2f}s for {person_name}")

    # --- Step D: Build Record and Save ---
    record_obj = {
        "index": index,
        "input_row": row_data, # Maybe rename for clarity
        "external_raw_data": {
            "research_files_included": research_files,
            "raw_research_content": raw_research_content if raw_research_content else None
        },
        "enriched_data": enriched_data if enriched_data else None,
        "supplemental_context_summary": research_summary,
        "grok_final_bio": final_bio_text
    }

    save_start = time.time()
    safe_name = sanitize_filename(person_name)
    out_json_path = os.path.join(OUTPUT_DATA_DIR, safe_name + ".json")
    out_txt_path = os.path.join(BIOS_DIR, safe_name + ".txt")

    # Write JSON output
    try:
        os.makedirs(OUTPUT_DATA_DIR, exist_ok=True) # Ensure dir exists
        with open(out_json_path, "w", encoding="utf-8") as jf:
            json.dump(record_obj, jf, ensure_ascii=False, indent=2)
        # logging.info(f"Saved JSON record to {out_json_path}")
    except Exception as e:
        logging.error(f"Error writing JSON for {person_name} to {out_json_path}: {e}")

    # Write TXT biography
    try:
        os.makedirs(BIOS_DIR, exist_ok=True) # Ensure dir exists
        with open(out_txt_path, "w", encoding="utf-8") as tf:
            # Only write bio if it's not an error message
            if not final_bio_text.startswith("Error:"):
                 tf.write(final_bio_text)
            else:
                 tf.write(f"Failed to generate biography. Error: {final_bio_text}")
        # logging.info(f"Saved biography text to {out_txt_path}")
    except Exception as e:
        logging.error(f"Error writing TXT bio for {person_name} to {out_txt_path}: {e}")

    save_end = time.time()
    # logging.info(f"Saving outputs took {save_end - save_start:.2f}s")

    row_end_time = time.time()
    logging.info(f"--- Finished processing {person_name} in {row_end_time - row_start_time:.2f}s ---")

    # Return status or identifier
    return f"Successfully processed: {person_name}"


# ==========================
# 7) Main Execution Block
# ==========================
def main():
    overall_start_time = time.time()
    logging.info(f"Starting script execution with MAX_WORKERS={MAX_WORKERS}")

    # Ensure output directories exist
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
    os.makedirs(BIOS_DIR, exist_ok=True)

    # Load input CSV
    try:
        # Explicitly treat all columns as strings, handle NA values
        df = pd.read_csv(INPUT_CSV_PATH, dtype=str, keep_default_na=False)
        # df.fillna('', inplace=True) # Already handled by keep_default_na=False + dtype=str
    except FileNotFoundError:
        logging.error(f"Input CSV not found: {INPUT_CSV_PATH}")
        return
    except Exception as e:
        logging.error(f"Error reading or processing CSV {INPUT_CSV_PATH}: {e}")
        return

    total_rows = len(df)
    if total_rows == 0:
        logging.info("Input CSV is empty. Exiting.")
        return

    logging.info(f"Loaded {total_rows} rows from {INPUT_CSV_PATH}. Starting concurrent processing.")

    successful_count = 0
    failed_count = 0

    # Use ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Create future tasks
        future_to_index = {executor.submit(process_row, df.iloc[i].to_dict(), i, total_rows): i for i in range(total_rows)}

        # Process futures as they complete
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            person_name = safe_get(df.iloc[index].to_dict(), 'full_name', f"Row_{index+1}")
            try:
                result = future.result() # Get the result (or exception)
                logging.info(f"Future completed for index {index} ({person_name}): {result}")
                if "Successfully processed" in result:
                    successful_count += 1
                else: # Should not happen if exceptions are caught, but as fallback
                    failed_count += 1
            except Exception as exc:
                logging.error(f"!!! Processing generated an exception for index {index} ({person_name}): {exc}", exc_info=True) # Log traceback
                failed_count += 1

    overall_end_time = time.time()
    total_duration = overall_end_time - overall_start_time

    logging.info("=" * 50)
    logging.info(f"Script finished processing {total_rows} rows.")
    logging.info(f"Successful: {successful_count}, Failed: {failed_count}")
    logging.info(f"Total execution time: {total_duration:.2f} seconds ({total_duration / 60:.2f} minutes)")
    logging.info(f"Average time per row: {total_duration / total_rows:.2f} seconds (approx, depends on concurrency)")
    logging.info(f"JSON records saved in: '{OUTPUT_DATA_DIR}'")
    logging.info(f"Final biographies saved in: '{BIOS_DIR}'")
    logging.info("=" * 50)


if __name__ == "__main__":
    # Make sure API keys are loaded before initializing clients that need them
    if not PERPLEXITY_API_KEY: logging.warning("PERPLEXITY_API_KEY environment variable not set.")
    if not XAI_API_KEY: logging.warning("XAI_API_KEY environment variable not set. Grok bio generation will be skipped.")

    # Initialize Grok client here if key exists, handles potential error during init
    if XAI_API_KEY and not grok_client:
         try:
             grok_client = OpenAI(api_key=XAI_API_KEY, base_url=GROK_ENDPOINT_BASE)
             logging.info("Grok client initialized successfully.")
         except Exception as e:
             logging.error(f"Failed to initialize Grok client in main block: {e}")
             grok_client = None # Ensure it remains None

    main()