#!/usr/bin/env python3
"""
Comprehensive Research Script - Combines web research with LinkedIn/email enrichment
Replaces the "Ultimate Exhaustive Research" Cursor workflow
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import our research modules
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from web_research import conduct_research
from linkedin_enhance import run_linkedin_research
from enrich_email import get_enrich_so_data

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def comprehensive_research(figure_name, context=None, refresh=False, linkedin_url=None, email=None):
    """Conduct comprehensive research using all available data sources."""
    logging.info(f"Starting comprehensive research for {figure_name}...")
    
    research_dir = Path("research") / figure_name
    research_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Web Research
    logging.info("Phase 1: Web Research")
    dossier_path = conduct_research(figure_name, context, refresh)
    if not dossier_path:
        logging.warning("Web research failed or skipped")
    
    # Step 2: Email Enrichment (if email provided)
    enriched_data = None
    if email:
        logging.info("Phase 2: Email Enrichment")
        enriched_data = get_enrich_so_data(email)
        if enriched_data and enriched_data.get("success"):
            logging.info(f"✅ Enriched data retrieved for {email}")
            # Save enriched data
            enriched_path = research_dir / "enriched_data.json"
            import json
            with open(enriched_path, "w", encoding="utf-8") as f:
                json.dump(enriched_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Enriched data saved to {enriched_path}")
            
            # Update LinkedIn URL if discovered via email
            if not linkedin_url and enriched_data.get("linkedin"):
                linkedin_url = enriched_data.get("linkedin")
                logging.info(f"LinkedIn URL discovered via email enrichment: {linkedin_url}")
        else:
            logging.warning("Email enrichment failed or returned no data")
    
    # Step 3: LinkedIn Enhancement (if LinkedIn URL available)
    if linkedin_url:
        logging.info("Phase 3: LinkedIn Enhancement")
        try:
            linkedin_result = run_linkedin_research(figure_name, linkedin_url)
            if linkedin_result and linkedin_result.get("success"):
                logging.info("✅ LinkedIn enhancement completed")
                # Save LinkedIn data
                linkedin_path = research_dir / "linkedin_data.json"
                import json
                with open(linkedin_path, "w", encoding="utf-8") as f:
                    json.dump(linkedin_result, f, indent=2, ensure_ascii=False)
                logging.info(f"LinkedIn data saved to {linkedin_path}")
            else:
                logging.warning("LinkedIn enhancement failed")
        except Exception as e:
            logging.error(f"LinkedIn enhancement error: {e}")
    
    # Step 4: Data Integration Summary
    logging.info("Phase 4: Data Integration Complete")
    summary_path = research_dir / "research_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Research Summary: {figure_name}\n\n")
        f.write(f"## Data Sources Used\n\n")
        f.write(f"- ✅ Web Research: {'Completed' if dossier_path else 'Skipped/Failed'}\n")
        f.write(f"- ✅ Email Enrichment: {'Completed' if enriched_data and enriched_data.get('success') else 'Skipped/Failed'}\n")
        f.write(f"- ✅ LinkedIn Enhancement: {'Completed' if linkedin_url else 'Skipped'}\n\n")
        f.write(f"## Output Files\n\n")
        if dossier_path:
            f.write(f"- Dossier: {dossier_path}\n")
        if enriched_data:
            f.write(f"- Enriched Data: research/{figure_name}/enriched_data.json\n")
        if linkedin_url:
            f.write(f"- LinkedIn Data: research/{figure_name}/linkedin_data.json\n")
    
    logging.info(f"✅ Comprehensive research complete. Summary: {summary_path}")
    return summary_path


def main():
    parser = argparse.ArgumentParser(description="Conduct comprehensive research on a public figure")
    parser.add_argument("figure_name", help="Name of the public figure to research")
    parser.add_argument("--context", help="Optional context for disambiguation")
    parser.add_argument("--refresh", action="store_true", help="Force fresh research")
    parser.add_argument("--linkedin", help="LinkedIn URL for enhancement")
    parser.add_argument("--email", help="Email address for Enrich.so enrichment")
    
    args = parser.parse_args()
    
    result = comprehensive_research(
        args.figure_name,
        context=args.context,
        refresh=args.refresh,
        linkedin_url=args.linkedin,
        email=args.email
    )
    
    if result:
        print(f"✅ Comprehensive research complete: {result}")
        sys.exit(0)
    else:
        print("❌ Research failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

