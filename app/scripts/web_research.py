#!/usr/bin/env python3
"""
Web Research Script - Replaces Cursor workflow web research functionality
Uses Perplexity API to conduct comprehensive web research on a public figure.
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from perplexity import Perplexity
import requests

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def search_perplexity(client, query, identity):
    """
    Search using Perplexity API and return results only if they match the target identity.
    identity = {
        "name": "...",
        "title": "...",
        "description": "...",
        "url": "..."
    }
    """
    try:
        system_prompt = f"""
You are a research assistant.

Target person (must match exactly):
Name: {identity['name']}
LinkedIn headline: {identity['title']}
Description: {identity['description']}
Profile URL: {identity['url']}

Rules:
1. Only return information that clearly refers to this same or similar individual.
2. If multiple people share this name, discard unrelated ones.
3. Verify using role, industry, and description.
4. If identity cannot be confirmed, reply exactly with: IDENTITY_NOT_CONFIRMED.
5. Do NOT mix data from different people.


"""

        completion = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=2000,
            temperature=0.1
        )

        result = completion.choices[0].message.content
        logging.info(f"SYSTEM PROMPT {system_prompt} RESULT DATA {result}")
        # Optional guard
        if "IDENTITY_NOT_CONFIRMED" in result:
            return ""

        return result

    except Exception as e:
        logging.error(f"Perplexity search failed for query '{query}': {e}")
        return None


def research_phase(client, figure_name,identity, context=None, phase_name="", search_queries=None):
    """Conduct a research phase with multiple search queries."""
    if not search_queries:
        return ""
    
    logging.info(f"Starting {phase_name} research for {figure_name}...")
    results = []
    
    for i, query_template in enumerate(search_queries, 1):
        query = query_template.format(figure=figure_name, context=context or "")
       
        logging.info(f"  Query {i}/{len(search_queries)}: {query}...")
        result = search_perplexity(client, query,identity)
        # save to research data columns 
        if result:
            results.append(f"### Search {i}: {query}\n\n{result}\n\n")
        # Small delay to avoid rate limits
        import time
        time.sleep(1)
    
    combined = "\n".join(results)
    logging.info(f"Completed {phase_name} research ({len(results)} queries)")
    return combined


def conduct_research(figure_name, context=None, refresh=False,research_sources=None):
    """Conduct comprehensive web research on a public figure."""
    if not PERPLEXITY_API_KEY:
        logging.error("PERPLEXITY_API_KEY not set. Cannot conduct web research.")
        return None
    
    # Initialize Perplexity client
    try:
        client = Perplexity(api_key=PERPLEXITY_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize Perplexity client: {e}")
        return None
    
    research_dir = Path("research") / figure_name
    research_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if research exists and refresh flag
    dossier_path = research_dir / "dossier.md"
    if dossier_path.exists() and not refresh:
        logging.info(f"Research already exists for {figure_name}. Use --refresh to overwrite.")
        return str(dossier_path)
    
    logging.info(f"Starting comprehensive research for {figure_name}...")
    
    # Phase 1: Identity & Biography
    # bio_queries = [
    #     f'site:linkedin.com/in/ "{figure_name}"',
    #     f'site:wikipedia.org "{figure_name}"',
    #     f'site:crunchbase.com "{figure_name}"',
    #     f'"{figure_name}" biography OR "about" OR "profile"',
    #     f'"{figure_name}" CEO OR founder OR executive',
    #     f'"{figure_name}" interview OR profile OR feature'
    # ]
    bio_queries=[]
    for source in research_sources:
        bio_queries.append(f"site:{source} {figure_name}")

    bio_content = research_phase(client, figure_name, context, "Biography", bio_queries)

    
    # Phase 2: Media Sweep
    # media_queries = [
    #     f'site:youtube.com "{figure_name}" interview OR talk OR speech',
    #     f'site:spotify.com OR site:apple.com/podcasts "{figure_name}"',
    #     f'"{figure_name}" video OR webinar OR presentation',
    #     f'"{figure_name}" interview OR conversation OR discussion',
    #     f'"{figure_name}" conference OR summit OR keynote',
    #     f'"{figure_name}" TV OR television OR news'
    # ]
    media_queries=[]
    for source in research_sources:
        media_queries.append(f"site:{source} {figure_name} interview OR talk OR speech OR TV OR television OR news")
    media_content = research_phase(client, figure_name, context, "Media", media_queries)
    
    # Phase 3: Publications
    pub_queries = [
        f'"{figure_name}" book OR author OR published',
        # f'"{figure_name}" article OR blog OR writing',
        # f'"{figure_name}" research OR study OR paper',
        # f'"{figure_name}" whitepaper OR report OR analysis',
        # f'site:patents.google.com "{figure_name}"',
        # f'site:medium.com OR site:substack.com "{figure_name}"'
    ]
    pub_content = research_phase(client, figure_name, context, "Publications", pub_queries)
    
    # Phase 4: Quotes
    quote_queries = [
        # f'"{figure_name}" quotes OR sayings OR wisdom',
        # f'"{figure_name}" said OR stated OR mentioned',
        f'site:twitter.com OR site:linkedin.com "{figure_name}"',
        # f'"{figure_name}" speech OR presentation OR keynote',
        # f'"{figure_name}" quote OR insight OR perspective'
    ]
    quote_content = research_phase(client, figure_name, context, "Quotes", quote_queries)
    
    # Phase 5: Frameworks
    framework_queries = [
        # f'"{figure_name}" framework OR model OR methodology',
        # f'"{figure_name}" process OR system OR approach',
        # f'"{figure_name}" strategy OR method OR technique',
        # f'"{figure_name}" concept OR theory OR principle',
        # f'"{figure_name}" tool OR technique OR practice',
        f'"{figure_name}" philosophy OR mindset OR thinking'
    ]
    framework_content = research_phase(client, figure_name, context, "Frameworks", framework_queries)
    
    # Phase 6: Themes
    theme_queries = [
        f'"{figure_name}" values OR beliefs OR principles',
        # f'"{figure_name}" mission OR purpose OR vision',
        # f'"{figure_name}" philosophy OR worldview OR perspective',
        # f'"{figure_name}" passionate OR interested OR focused',
        # f'"{figure_name}" concerned OR worried OR focused on',
        # f'"{figure_name}" goal OR objective OR aim'
    ]
    theme_content = research_phase(client, figure_name, context, "Themes", theme_queries)
    
    # Compile dossier
    dossier = f"""# Research Dossier: {figure_name}

{f"*Context: {context}*" if context else ""}

## Biography & Professional Identity

{bio_content}

## Media Appearances & Interviews

{media_content}

## Publications & Written Works

{pub_content}

## Direct Quotes & Insights

{quote_content}

## Frameworks & Methodologies

{framework_content}

## Recurring Themes & Philosophy

{theme_content}

## Research Notes

*This dossier was generated using automated web research. Please verify all information and sources.*
"""
    
    # Save dossier
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write(dossier)
    
    logging.info(f"Research dossier saved to {dossier_path}")
    return {
        "bio_content":bio_content,
        "media_content":media_content,
        "pub_content":pub_content,
        "quote_content":quote_content,
        "framework_content":framework_content,
        "theme_content":theme_content,
        "dossier_path":str(dossier_path)
    }
    # return str(dossier_path)



from urllib.parse import urlparse

def canonical_linkedin_url(url: str) -> str:
    """
    Normalize LinkedIn profile URLs so regional domains match.
    """
    if not url:
        return ""

    parsed = urlparse(url)

    # Force canonical domain
    domain = "linkedin.com"

    # Keep only path (e.g. /in/jharna-agrawal)
    path = parsed.path.rstrip("/")

    return f"https://{domain}{path}"

from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


from urllib.parse import urlparse

def extract_linkedin_slug(value: str) -> str:
    """
    Extract LinkedIn profile slug from a URL or partial input.
    Examples:
      linkedin.com/in/shaktiprasad -> shaktiprasad
      https://www.linkedin.com/in/shakti-prasad-k -> shakti-prasad-k
    """
    if not value:
        return ""

    # Ensure it parses as a URL
    if not value.startswith("http"):
        value = "https://" + value

    parsed = urlparse(value)

    parts = parsed.path.strip("/").split("/")

    if len(parts) >= 2 and parts[0] == "in":
        return parts[1].lower()

    return ""


def search_firecrawl(query: str):
    logging.info(f"Searching Firecrawl with query: {query}")

    url = "https://api.firecrawl.dev/v2/search"

    payload = {
        "query": query,
        "sources": ["web"],
        "limit": 5
    }

    headers = {
        "Authorization": "Bearer fc-08fb6666bf5c4c97962b4b7645ee79d9",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    logging.info(f"full firecrawl response:{data}")

    web_data = data.get("data", {}).get("web", [])

    query_slug = extract_linkedin_slug(query)
    logging.info(f"Extracted query slug: {query_slug}")

    filtered = [
        item for item in web_data
        if extract_linkedin_slug(item.get("url", "")) == query_slug
    ]

    logging.info(f"Filtered Firecrawl results: {filtered}")

    return filtered





def format_firecrawl_results(results, source_label="Web Search"):
    if not results:
        return ""

    blocks = []
    for i, item in enumerate(results, 1):
        blocks.append(
            f"""### {source_label} Result {i}

            **Title:** {item.get("title", "N/A")}
            **URL:** {item.get("url", "N/A")}

            {item.get("markdown") or item.get("content") or item.get("description") or ""}
            """
                    )

    return "\n".join(blocks)




def build_identity_clause(figure_name, clues):
    clauses = []

    if clues["organizations"]:
        clauses.append(
            "(" + " OR ".join(f'"{o}"' for o in list(clues["organizations"])[:3]) + ")"
        )

    if clues["roles"]:
        clauses.append(
            "(" + " OR ".join(f'"{r}"' for r in list(clues["roles"])[:3]) + ")"
        )

    if clues["skills"]:
        clauses.append(
            "(" + " OR ".join(f'"{s}"' for s in list(clues["skills"])[:3]) + ")"
        )

    if not clauses:
        return f'"{figure_name}"'

    return f'"{figure_name}" AND ' + " AND ".join(clauses)


def extract_identity_clues_from_firecrawl(firecrawl_raw):
    clues = {
        "roles": set(),
        "organizations": set(),
        "skills": set(),
        "keywords": set(),
    }

    for item in firecrawl_raw:
        title = (item.get("title") or "").lower()
        desc = (item.get("description") or "").lower()
        text = f"{title} {desc}"

        # roles
        for role in [
            "ceo", "founder", "co-founder",
            "sde", "software engineer", "developer",
            "full-stack", "backend", "frontend",
            "engineer", "architect"
        ]:
            if role in text:
                clues["roles"].add(role)

        # organizations (very important)
        if " at " in text:
            parts = text.split(" at ")
            if len(parts) > 1:
                org = parts[1].split(" ")[0:3]
                clues["organizations"].add(" ".join(org))

        # skills (useful secondary anchors)
        for skill in [
            "kubernetes", "docker", "distributed systems",
            "microservices", "cloud", "python", "java"
        ]:
            if skill in text:
                clues["skills"].add(skill)

        # keep original tokens too
        clues["keywords"].update(text.split())

    return clues





def conduct_research_copy(figure_name, context=None, refresh=True,research_sources=None, linkedin=None,twitter=None, youtube=None, name=None,title=None,bio=None):
    """Conduct comprehensive web research on a public figure."""
    if not PERPLEXITY_API_KEY:
        logging.error("PERPLEXITY_API_KEY not set. Cannot conduct web research.")
        return None
    
    # Initialize Perplexity client
    try:
        client = Perplexity(api_key=PERPLEXITY_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize Perplexity client: {e}")
        return None
    
    research_dir = Path("static/research") / figure_name
    research_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if research exists and refresh flag
    dossier_path = research_dir / "dossier.md"
    if dossier_path.exists() and not refresh:
        logging.info(f"Research already exists for {figure_name}. Use --refresh to overwrite.")
        return str(dossier_path)
    
    logging.info(f"Starting comprehensive research for {figure_name}...")

    
    
    # Phase 1: Identity & Biography
    linkedin_site = f"{linkedin} {figure_name}" if linkedin else f'site:linkedin.com "{figure_name}"'

    twitter_site = f"{twitter} {figure_name}" if twitter else f'site:x.com "{figure_name}"'


    firecrawl_sections = []
    firecrawl_raw = [] 

    if linkedin:
        try:

            fc_data = search_firecrawl(query=linkedin)
            firecrawl_raw.extend(fc_data)
            logging.info(f"linkedin firecrawl data:{fc_data}")
            firecrawl_sections.append(
                format_firecrawl_results(fc_data, source_label="LinkedIn (Firecrawl)")
            )
        
        except Exception as e:
            logging.info(f"error at search crawl:{str(e)}")

    if twitter:

        try:

            fc_data = search_firecrawl(query=twitter)
            firecrawl_raw.extend(fc_data)
            logging.info(f"twitter firecrawl data:{fc_data}")
            firecrawl_sections.append(
                format_firecrawl_results(fc_data, source_label="Twitter/X (Firecrawl)")
            )
        except Exception as e:
            logging.info(f"error at search crawl:{str(e)}")

    

    try:
        for source in research_sources:
            fc_data = search_firecrawl(query=source)
            firecrawl_raw.extend(fc_data)
            logging.info(f"{source} firecrawl data:{fc_data}")
            firecrawl_sections.append(
                format_firecrawl_results(fc_data, source_label=source)
            )

    
    except Exception as e:
        logging.info(f"error at search crawl:{str(e)}")


    

    firecrawl_content = "\n".join(firecrawl_sections)
    if len(firecrawl_raw)>0:
        identity = {
        "name": figure_name,
        "title": firecrawl_raw[0]["title"],
        "description": firecrawl_raw[0]["description"],
        "url": firecrawl_raw[0]["url"]
        }
    
    else:
        identity = {
        "name": name,
        "title": title,
        "description": bio,
        "url": ""
        }

    
    logging.info(f"Identity created:{identity}")


    bio_queries = [
        linkedin_site,
        twitter_site,
        f'site:wikipedia.org "{figure_name}"',
        f'site:crunchbase.com "{figure_name}"',
        f'"{figure_name}" biography OR "about" OR "profile"',
        f'"{figure_name}" CEO OR founder OR executive',
        f'"{figure_name}" interview OR profile OR feature'
    ]
    bio_queries=[]
    for source in research_sources:
        bio_queries.append(f"site:{source}")

    bio_content = research_phase(client, figure_name,identity, context, "Biography", bio_queries)
  
    
    # Phase 2: Media Sweep
    # identity_clues = extract_identity_clues_from_firecrawl(firecrawl_raw)
    # identity_clause = build_identity_clause(figure_name, identity_clues)

    youtube_site = f"site:{youtube} '{figure_name}'" if youtube else f'site:youtube.com "{figure_name}" interview OR talk OR speech'
    


    media_queries = [
        youtube_site,
        f'site:spotify.com OR site:apple.com/podcasts "{figure_name}"',
        f'"{figure_name}" video OR webinar OR presentation',
        f'"{figure_name}" interview OR conversation OR discussion',
        f'"{figure_name}" conference OR summit OR keynote',
        f'"{figure_name}" TV OR television OR news'
    ]
    media_queries=[]
    for source in research_sources:
        media_queries.append(f"site:{source} {figure_name} interview OR talk OR speech OR TV OR television OR news")
    media_content = research_phase(client, figure_name,identity, context, "Media", media_queries)
    
    # Phase 3: Publications
    pub_queries = [
        f'"{figure_name}" book OR author OR published',
        f'"{figure_name}" article OR blog OR writing',
        f'"{figure_name}" research OR study OR paper',
        f'"{figure_name}" whitepaper OR report OR analysis',
        f'site:patents.google.com "{figure_name}"',
        f'site:medium.com OR site:substack.com "{figure_name}"'
    ]
    # pub_content = research_phase(client, figure_name,identity, context, "Publications", pub_queries)
    pub_content=""
    
    # Phase 4: Quotes
    quote_queries = [
        f'"{figure_name} " quotes OR sayings OR wisdom',
        f'"{figure_name}" said OR stated OR mentioned',
        twitter_site+" quotes OR sayings OR wisdom",
        linkedin_site+" quotes OR sayings OR wisdom",
        f'"{figure_name}" speech OR presentation OR keynote',
        f'"{figure_name}" quote OR insight OR perspective'
    ]
    # quote_content = research_phase(client, figure_name,identity, context, "Quotes", quote_queries)
    quote_content =""
    
    # Phase 5: Frameworks
    framework_queries = [
        f'"{figure_name}" framework OR model OR methodology',
        f'"{figure_name}" process OR system OR approach',
        f'"{figure_name}" strategy OR method OR technique',
        f'"{figure_name}" concept OR theory OR principle',
        f'"{figure_name}" tool OR technique OR practice',
        f'"{figure_name}" philosophy OR mindset OR thinking'
    ]
    # framework_content = research_phase(client, figure_name,identity, context, "Frameworks", framework_queries)
    framework_content =""
    
    # Phase 6: Themes
    theme_queries = [
        f'"{figure_name}" values OR beliefs OR principles',
        f'"{figure_name}" mission OR purpose OR vision',
        f'"{figure_name}" philosophy OR worldview OR perspective',
        f'"{figure_name}" passionate OR interested OR focused',
        f'"{figure_name}" concerned OR worried OR focused on',
        f'"{figure_name}" goal OR objective OR aim'
    ]
    # theme_content = research_phase(client, figure_name, identity,context, "Themes", theme_queries)
    theme_content =""
    # Compile dossier
    dossier = f"""# Research Dossier: {figure_name}

{f"*Context: {context}*" if context else ""}

## Biography & Professional Identity

{bio_content}


## Priority Profile Data (Firecrawl)

{firecrawl_content}

## Media Appearances & Interviews

{media_content}

## Publications & Written Works

{pub_content}

## Direct Quotes & Insights

{quote_content}

## Frameworks & Methodologies

{framework_content}

## Recurring Themes & Philosophy

{theme_content}

## Research Notes

*This dossier was generated using automated web research. Please verify all information and sources.*
"""
    
    # Save dossier
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write(dossier)
    
    logging.info(f"Research dossier saved to {dossier_path}")
    return {
        "bio_content":bio_content,
        "media_content":media_content,
        "pub_content":pub_content,
        "quote_content":quote_content,
        "framework_content":framework_content,
        "theme_content":theme_content,
        "dossier_path":str(dossier_path)
    }
    # return str(dossier_path)





def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Conduct web research on a public figure")
    parser.add_argument("figure_name", help="Name of the public figure to research")
    parser.add_argument("--context", help="Optional context for disambiguation")
    parser.add_argument("--refresh", action="store_true", help="Force fresh research (overwrite existing)")
    
    args = parser.parse_args()
    
    result = conduct_research(args.figure_name, args.context, args.refresh)
    if result:
        print(f"✅ Research complete: {result}")
        sys.exit(0)
    else:
        print("❌ Research failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

