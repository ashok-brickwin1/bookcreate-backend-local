#!/usr/bin/env python3
"""
Book Outline Generator - Replaces Cursor workflow outline generation
Uses Grok to generate a 12-chapter book outline from research files.
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()
GROK_ENDPOINT_BASE = "https://api.x.ai/v1"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import logging, secrets, string
from app.core.utils import send_email


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_research_files(figure_name):
    """Load all research files for a figure."""
    research_dir = Path("research") / figure_name
    if not research_dir.exists():
        logging.warning(f"Research directory not found: {research_dir}")
        return {}
    
    files = {}
    priority_order = [
        "interview.txt",
        "dossier.md",
        "bio.md",
        "media.md",
        "publications.md",
        "quotes.md",
        "frameworks.md",
        "themes.md",
        "sources.md"
    ]
    
    for filename in priority_order:
        filepath = research_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                files[filename] = f.read()
            logging.info(f"Loaded {filename}")
    
    return files


def generate_outline(figure_name, research_files):
    """Generate book outline using Grok."""
    if not XAI_API_KEY:
        logger.error("XAI_API_KEY not set. Cannot generate outline.")
        return None
    
    try:
        client = OpenAI(api_key=XAI_API_KEY, base_url=GROK_ENDPOINT_BASE)
    except Exception as e:
        logger.error(f"Failed to initialize Grok client: {e}")
        return None
    
    # Build context from research files
    context_parts = []
    
    # Priority: interview.txt if available
    if "interview.txt" in research_files:
        context_parts.append(f"=== PRIMARY SOURCE: Interview Transcript ===\n{research_files['interview.txt']}\n")
    
    # Add other research files
    for filename in ["dossier.md", "bio.md", "media.md", "publications.md", "quotes.md", "frameworks.md", "themes.md"]:
        if filename in research_files:
            context_parts.append(f"=== {filename.upper().replace('.', ' ')} ===\n{research_files[filename]}\n")
    
    full_context = "\n".join(context_parts)
    
    # Truncate if too long (Grok has limits)
    MAX_CONTEXT = 50000
    if len(full_context) > MAX_CONTEXT:
        logging.warning(f"Context too long ({len(full_context)}), truncating to {MAX_CONTEXT}")
        full_context = full_context[:MAX_CONTEXT] + "\n\n[Context truncated...]"
    
    system_prompt = """You are Book Architect, a world-class ghostwriter and nonfiction book strategist. 
You create comprehensive book outlines in the authentic voice of the subject, using their actual words, 
frameworks, and perspectives from the research materials provided."""
    
    user_prompt = f"""Create a full 12-chapter book outline for {figure_name} using the research materials below.

**Structure Required:**

**Introduction:**
- Book Title
- Core Focus
- Opening Story
- 5 Big Ideas
- 5 Direct Quotes

**Chapters 1-12:**
For each chapter:
- Chapter Title
- Core Focus (transformational concept)
- Opening Story (real moment or case study)
- 5 Big Ideas
- 5 Direct Quotes

**Requirements:**
- At least 2,000 words total
- Each section must have exactly 5 Big Ideas + 5 Direct Quotes
- Absolutely no fabricated quotes or filler
- Must feel as if {figure_name} wrote it themselves
- If interview transcript exists, prioritize its content for voice, tone, and direct quotes
- Use other research files to support and supplement

**Research Materials:**
{full_context}

**Book Outline:**
"""
    
    try:
        completion = client.chat.completions.create(
            model="grok-4-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        outline = completion.choices[0].message.content.strip()
        return outline
    except Exception as e:
        logging.error(f"Failed to generate outline: {e}")
        return None


def generate_outline_copy(figure_name, research_files, no_of_chapters,context):
    """Generate book outline using Grok."""
    logger.info("generate outline copy called")
    no_of_chapters=2
    if not XAI_API_KEY:
        logger.error("XAI_API_KEY not set. Cannot generate outline.")
        return None
    
    try:
        client = OpenAI(api_key=XAI_API_KEY, base_url=GROK_ENDPOINT_BASE)
    except Exception as e:
        logging.error(f"Failed to initialize Grok client: {e}")
        return None
    
    # Build context from research files
    context_parts = []
    
    # Priority: interview.txt if available
    if "interview.txt" in research_files:
        context_parts.append(f"=== PRIMARY SOURCE: Interview Transcript ===\n{research_files['interview.txt']}\n")
    
    # Add other research files
    for filename in ["dossier.md", "bio.md", "media.md", "publications.md", "quotes.md", "frameworks.md", "themes.md"]:
        if filename in research_files:
            logger.info(f"filename:{filename} exist in generate outline function")
            context_parts.append(f"=== {filename.upper().replace('.', ' ')} ===\n{research_files[filename]}\n")
    
    # full_context = "\n".join(context_parts).join("/n").join(context) 
    full_context = ""

    if context_parts:
        full_context += "\n\n".join(context_parts)

    if context:
        full_context += "\n\n=== USER ANSWERS & LIFE MOMENTS ===\n"
        full_context += context if isinstance(context, str) else json.dumps(context, indent=2)
        
    # Truncate if too long (Grok has limits)
    MAX_CONTEXT = 5000
    if len(full_context) > MAX_CONTEXT:
        logging.warning(f"Context too long ({len(full_context)}), truncating to {MAX_CONTEXT}")
        full_context = full_context[:MAX_CONTEXT] + "\n\n[Context truncated...]"
    
    system_prompt = """You are Book Architect, a world-class ghostwriter and nonfiction book strategist. 
You create comprehensive book outlines in the authentic voice of the subject, using their actual words, 
frameworks, and perspectives from the research materials provided."""
    
#     user_prompt = f"""Create a full {no_of_chapters}-chapter book outline for {figure_name} using the research materials below.

# **Structure Required:**

# **Introduction:**
# - Book Title
# - Core Focus
# - Opening Story
# - 1 Big Ideas
# - 1 Direct Quotes

# **Chapters 1-{no_of_chapters}:**
# For each chapter:
# - Chapter Title
# - Core Focus (transformational concept)
# - Opening Story (real moment or case study)
# - 1 Big Ideas
# - 1 Direct Quotes

# **Requirements:**
# - At least 500 words total
# - Each section must have exactly 1 Big Ideas + 1 Direct Quotes
# - Absolutely no fabricated quotes or filler
# - Must feel as if {figure_name} wrote it themselves
# - If interview transcript exists, prioritize its content for voice, tone, and direct quotes
# - Use other research files to support and supplement

# **Research Materials:**
# {full_context}

# **Book Outline:**
# """
    
    user_prompt = f"""
You must return ONLY valid JSON.
Do NOT include markdown, explanations, commentary, or extra text.
Do NOT wrap the output in ``` blocks.

Generate a structured book outline in the following EXACT JSON schema:

{{
  "book_title": "string",
  "introduction": {{
    "core_focus": "string",
    "opening_story": "string",
    "big_idea": "string",
    "direct_quote": "string"
  }},
  "chapters": [
    {{
      "chapter_number": number,
      "chapter_title": "string",
      "core_focus": "string",
      "opening_story": "string",
      "big_idea": "string",
      "direct_quote": "string"
    }}
  ]
}}

Rules:
- Create exactly {no_of_chapters} chapters
- Each chapter must contain REAL content derived from the provided materials
- Use the subject's authentic voice
- Do NOT invent quotes — only reuse phrases that appear in the provided materials
- Avoid fluff, filler, or generic language
- Maintain narrative continuity across chapters

Subject:
{figure_name}

Research Materials:
{full_context}

Now return the JSON object only.
"""

    try:
        completion = client.chat.completions.create(
            model="grok-4-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        outline = completion.choices[0].message.content.strip()
        return outline
    except Exception as e:
        logging.error(f"Failed to generate outline: {e}")
        return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate book outline from research")
    parser.add_argument("figure_name", help="Name of the public figure")
    
    args = parser.parse_args()
    
    # Load research files
    research_files = load_research_files(args.figure_name)
    if not research_files:
        logging.error(f"No research files found for {args.figure_name}")
        sys.exit(1)
    
    # Generate outline
    logging.info(f"Generating book outline for {args.figure_name}...")
    outline = generate_outline(args.figure_name, research_files)
    
    if outline:
        # Save outline
        book_dir = Path("book") / args.figure_name
        book_dir.mkdir(parents=True, exist_ok=True)
        
        outline_path = book_dir / f"{args.figure_name}-book-outline.md"
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write(f"# {args.figure_name} - Book Outline\n\n")
            f.write(outline)
        
        logging.info(f"✅ Outline saved to {outline_path}")
        print(f"✅ Outline generated: {outline_path}")
        sys.exit(0)
    else:
        logging.error("Failed to generate outline")
        sys.exit(1)


if __name__ == "__main__":
    main()

