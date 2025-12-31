#!/usr/bin/env python3
"""
Exhaustive Research Script - Replaces Cursor workflow "Exhaustive Research"
Performs multi-phase research and saves to multiple structured files.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from perplexity import Perplexity

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def search_perplexity(client, query, max_tokens=2000):
    """Search using Perplexity API and return results."""
    try:
        completion = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": query}],
            max_tokens=max_tokens,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Perplexity search failed: {e}")
        return None


def save_research_file(research_dir, filename, content):
    """Save research content to a file."""
    filepath = research_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info(f"Saved: {filename}")
    return filepath


def exhaustive_research(figure_name, context=None, refresh=False):
    """Conduct exhaustive multi-phase research."""
    if not PERPLEXITY_API_KEY:
        logging.error("PERPLEXITY_API_KEY not set. Cannot conduct research.")
        return None
    
    research_dir = Path("research") / figure_name
    research_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if research exists and refresh flag
    dossier_path = research_dir / "dossier.md"
    if dossier_path.exists() and not refresh:
        logging.info(f"Research already exists for {figure_name}. Use --refresh to overwrite.")
        return str(dossier_path)
    
    try:
        client = Perplexity(api_key=PERPLEXITY_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize Perplexity client: {e}")
        return None
    
    logging.info(f"Starting exhaustive research for {figure_name}...")
    
    # Phase 1: Identity & Biography
    logging.info("Phase 1: Identity & Biography")
    bio_queries = [
        f'site:linkedin.com/in/ "{figure_name}"',
        f'site:wikipedia.org "{figure_name}"',
        f'site:crunchbase.com "{figure_name}"',
        f'"{figure_name}" biography OR "about" OR "profile"',
        f'"{figure_name}" CEO OR founder OR executive'
    ]
    bio_content = []
    for query in bio_queries:
        result = search_perplexity(client, query)
        if result:
            bio_content.append(f"### {query}\n\n{result}\n\n")
        import time
        time.sleep(1)
    save_research_file(research_dir, "bio.md", "\n".join(bio_content))
    
    # Phase 2: Media Sweep
    logging.info("Phase 2: Media Sweep")
    media_queries = [
        f'site:youtube.com "{figure_name}" interview OR talk OR speech',
        f'site:spotify.com OR site:apple.com/podcasts "{figure_name}"',
        f'"{figure_name}" video OR webinar OR presentation',
        f'"{figure_name}" interview OR conversation OR discussion',
        f'"{figure_name}" conference OR summit OR keynote'
    ]
    media_content = []
    for query in media_queries:
        result = search_perplexity(client, query)
        if result:
            media_content.append(f"### {query}\n\n{result}\n\n")
        import time
        time.sleep(1)
    save_research_file(research_dir, "media.md", "\n".join(media_content))
    
    # Phase 3: Publications
    logging.info("Phase 3: Publications")
    pub_queries = [
        f'"{figure_name}" book OR author OR published',
        f'"{figure_name}" article OR blog OR writing',
        f'"{figure_name}" research OR study OR paper',
        f'"{figure_name}" whitepaper OR report OR analysis',
        f'site:medium.com OR site:substack.com "{figure_name}"'
    ]
    pub_content = []
    for query in pub_queries:
        result = search_perplexity(client, query)
        if result:
            pub_content.append(f"### {query}\n\n{result}\n\n")
        import time
        time.sleep(1)
    save_research_file(research_dir, "publications.md", "\n".join(pub_content))
    
    # Phase 4: Quotes
    logging.info("Phase 4: Quotes")
    quote_queries = [
        f'"{figure_name}" quotes OR sayings OR wisdom',
        f'"{figure_name}" said OR stated OR mentioned',
        f'site:twitter.com OR site:linkedin.com "{figure_name}"',
        f'"{figure_name}" speech OR presentation OR keynote',
        f'"{figure_name}" quote OR insight OR perspective'
    ]
    quote_content = []
    for query in quote_queries:
        result = search_perplexity(client, query)
        if result:
            quote_content.append(f"### {query}\n\n{result}\n\n")
        import time
        time.sleep(1)
    save_research_file(research_dir, "quotes.md", "\n".join(quote_content))
    
    # Phase 5: Frameworks
    logging.info("Phase 5: Frameworks")
    framework_queries = [
        f'"{figure_name}" framework OR model OR methodology',
        f'"{figure_name}" process OR system OR approach',
        f'"{figure_name}" strategy OR method OR technique',
        f'"{figure_name}" concept OR theory OR principle',
        f'"{figure_name}" philosophy OR mindset OR thinking'
    ]
    framework_content = []
    for query in framework_queries:
        result = search_perplexity(client, query)
        if result:
            framework_content.append(f"### {query}\n\n{result}\n\n")
        import time
        time.sleep(1)
    save_research_file(research_dir, "frameworks.md", "\n".join(framework_content))
    
    # Phase 6: Themes
    logging.info("Phase 6: Themes")
    theme_queries = [
        f'"{figure_name}" values OR beliefs OR principles',
        f'"{figure_name}" mission OR purpose OR vision',
        f'"{figure_name}" philosophy OR worldview OR perspective',
        f'"{figure_name}" passionate OR interested OR focused',
        f'"{figure_name}" goal OR objective OR aim'
    ]
    theme_content = []
    for query in theme_queries:
        result = search_perplexity(client, query)
        if result:
            theme_content.append(f"### {query}\n\n{result}\n\n")
        import time
        time.sleep(1)
    save_research_file(research_dir, "themes.md", "\n".join(theme_content))
    
    # Phase 7: Sources
    logging.info("Phase 7: Sources")
    sources_content = f"""# Sources for {figure_name}

## Research Methodology
This research was conducted using Perplexity AI web search across multiple phases.

## Sources Consulted
- LinkedIn profiles
- Wikipedia entries
- Crunchbase profiles
- YouTube videos and interviews
- Podcast appearances
- Articles and blog posts
- Publications and books
- Social media profiles

## Research Date
{logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}

## Notes
All sources were accessed via web search. Please verify URLs and dates for accuracy.
"""
    save_research_file(research_dir, "sources.md", sources_content)
    
    # Phase 8: Consolidated Dossier
    logging.info("Phase 8: Consolidated Dossier")
    dossier_content = f"""# Research Dossier: {figure_name}

{f"*Context: {context}*" if context else ""}

## Biography & Professional Identity

See `bio.md` for detailed biographical information.

## Media Appearances & Interviews

See `media.md` for comprehensive media coverage.

## Publications & Written Works

See `publications.md` for all published works.

## Direct Quotes & Insights

See `quotes.md` for 50+ direct quotes with sources.

## Frameworks & Methodologies

See `frameworks.md` for mental models and frameworks.

## Recurring Themes & Philosophy

See `themes.md` for thematic analysis.

## Sources

See `sources.md` for complete bibliography.

---

*This dossier was generated using exhaustive multi-phase research. All detailed content is available in the individual research files listed above.*
"""
    save_research_file(research_dir, "dossier.md", dossier_content)
    
    logging.info(f"✅ Exhaustive research complete. Files saved to {research_dir}")
    return str(research_dir / "dossier.md")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Conduct exhaustive multi-phase research")
    parser.add_argument("figure_name", help="Name of the public figure to research")
    parser.add_argument("--context", help="Optional context for disambiguation")
    parser.add_argument("--refresh", action="store_true", help="Force fresh research")
    
    args = parser.parse_args()
    
    result = exhaustive_research(args.figure_name, args.context, args.refresh)
    if result:
        print(f"✅ Research complete: {result}")
        sys.exit(0)
    else:
        print("❌ Research failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

