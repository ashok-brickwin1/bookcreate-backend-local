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

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def search_perplexity(client, query, max_results=5):
    """Search using Perplexity API and return results."""
    try:
        completion = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Perplexity search failed for query '{query}': {e}")
        return None


def research_phase(client, figure_name, context=None, phase_name="", search_queries=None):
    """Conduct a research phase with multiple search queries."""
    if not search_queries:
        return ""
    
    logging.info(f"Starting {phase_name} research for {figure_name}...")
    results = []
    
    for i, query_template in enumerate(search_queries, 1):
        query = query_template.format(figure=figure_name, context=context or "")
        logging.info(f"  Query {i}/{len(search_queries)}: {query[:80]}...")
        result = search_perplexity(client, query)
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







def conduct_research_copy(figure_name, context=None, refresh=False,research_sources=None):
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
    # pub_queries = [
    #     f'"{figure_name}" book OR author OR published',
    #     f'"{figure_name}" article OR blog OR writing',
    #     f'"{figure_name}" research OR study OR paper',
    #     f'"{figure_name}" whitepaper OR report OR analysis',
    #     f'site:patents.google.com "{figure_name}"',
    #     f'site:medium.com OR site:substack.com "{figure_name}"'
    # ]
    # pub_content = research_phase(client, figure_name, context, "Publications", pub_queries)
    pub_content=""
    
    # Phase 4: Quotes
    # quote_queries = [
    #     # f'"{figure_name}" quotes OR sayings OR wisdom',
    #     # f'"{figure_name}" said OR stated OR mentioned',
    #     # f'site:twitter.com OR site:linkedin.com "{figure_name}"',
    #     # f'"{figure_name}" speech OR presentation OR keynote',
    #     # f'"{figure_name}" quote OR insight OR perspective'
    # ]
    # quote_content = research_phase(client, figure_name, context, "Quotes", quote_queries)
    quote_content =""
    
    # Phase 5: Frameworks
    # framework_queries = [
    #     f'"{figure_name}" framework OR model OR methodology',
    #     f'"{figure_name}" process OR system OR approach',
    #     f'"{figure_name}" strategy OR method OR technique',
    #     f'"{figure_name}" concept OR theory OR principle',
    #     f'"{figure_name}" tool OR technique OR practice',
    #     f'"{figure_name}" philosophy OR mindset OR thinking'
    # ]
    # framework_content = research_phase(client, figure_name, context, "Frameworks", framework_queries)
    framework_content =""
    
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

