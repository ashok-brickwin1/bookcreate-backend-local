#!/bin/bash
# Run Research & Book Outline Workflows (Standalone - No Cursor Required)
# Usage:
#   ./scripts/run_outline.sh [workflow] [public_figure] [options]
#
# Workflows:
#   research     → Run "Deep Research Dossier" (web research, single dossier file)
#   exhaustive   → Run "Exhaustive Research" (multi-phase, multiple files)
#   auto         → Run "Deep Research + Book Outline" (web research + outline)
#   confirm      → Run "Research → Confirm → Outline" (web research + pause + outline)
#   batch        → Run "Batch Research" with CSV processing
#   enhanced     → Run "Enhanced Exhaustive Research" with LinkedIn integration
#   ultimate     → Run "Ultimate Exhaustive Research" with all data sources
#   enrich       → Run email enrichment only
#   expand       → Expand a single chapter from outline (requires --chapter="Title")
#   expand-all   → Expand all chapters from outline
#   compile      → Compile all chapters into a single manuscript
#
# Options:
#   --refresh    Force new research (archive old file first, then overwrite)
#   --auto       Skip manual pause in confirm workflow
#   --linkedin   Provide LinkedIn URL for enhanced research
#   --email      Provide email address for Enrich.so data
#
# Examples:
#   ./scripts/run_outline.sh research "Naval Ravikant"
#   ./scripts/run_outline.sh research "Naval Ravikant" --refresh
#   ./scripts/run_outline.sh exhaustive "Naval Ravikant" --refresh
#   ./scripts/run_outline.sh auto "Brené Brown" --refresh
#   ./scripts/run_outline.sh confirm "Tim Grover" --auto
#   ./scripts/run_outline.sh batch "input_people.csv"
#   ./scripts/run_outline.sh enhanced "Naval Ravikant" --linkedin="https://linkedin.com/in/naval"
#   ./scripts/run_outline.sh ultimate "Naval Ravikant" --email="naval@example.com"
#   ./scripts/run_outline.sh enrich "naval@example.com"
#   ./scripts/run_outline.sh expand "Naval Ravikant" --chapter="Chapter 1: The Path to Wealth"
#   ./scripts/run_outline.sh expand-all "Naval Ravikant"
#   ./scripts/run_outline.sh compile "Naval Ravikant"

WORKFLOW=$1
FIGURE=$2
shift 2
OPTIONS=$@

# Handle workflows that don't require a figure
if [ "$WORKFLOW" = "batch" ]; then
  CSV_FILE=$FIGURE
  if [ -z "$CSV_FILE" ]; then
    echo "❌ Usage: ./scripts/run_outline.sh batch [csv_file]"
    exit 1
  fi
elif [ "$WORKFLOW" = "enrich" ]; then
  EMAIL_ADDRESS=$FIGURE
  if [ -z "$EMAIL_ADDRESS" ]; then
    echo "❌ Usage: ./scripts/run_outline.sh enrich [email_address]"
    exit 1
  fi
elif [ -z "$WORKFLOW" ] || [ -z "$FIGURE" ]; then
  echo "❌ Usage: ./scripts/run_outline.sh [workflow] [public_figure] [options]"
  echo "   For batch: ./scripts/run_outline.sh batch [csv_file]"
  echo "   For enrich: ./scripts/run_outline.sh enrich [email_address]"
  exit 1
fi

DOSSIER="research/${FIGURE}.md"
ARCHIVE_DIR="research/archive"

# Handle refresh + archival
if [[ "$OPTIONS" == *"--refresh"* ]] && [ -f "$DOSSIER" ]; then
  mkdir -p "$ARCHIVE_DIR"
  TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
  mv "$DOSSIER" "$ARCHIVE_DIR/${FIGURE// /_}-$TIMESTAMP.md"
  echo "📦 Archived old dossier to $ARCHIVE_DIR/${FIGURE// /_}-$TIMESTAMP.md"
fi

case $WORKFLOW in
  research)
    echo "🔎 Running Deep Research Dossier for $FIGURE ..."
    python3 scripts/web_research.py "$FIGURE" $(echo "$OPTIONS" | grep -o '\--[^ ]*')
    ;;
  auto)
    echo "📝 Running Deep Research + Book Outline for $FIGURE ..."
    python3 scripts/web_research.py "$FIGURE" $(echo "$OPTIONS" | grep -o '\--[^ ]*')
    echo "📖 Generating book outline..."
    python3 scripts/generate_outline.py "$FIGURE"
    ;;
  confirm)
    echo "✅ Running Research → Confirm → Outline for $FIGURE ..."
    python3 scripts/web_research.py "$FIGURE" $(echo "$OPTIONS" | grep -o '\--[^ ]*')
    if [[ "$OPTIONS" != *"--auto"* ]]; then
      echo ""
      echo "📌 Research complete. Please review the dossier at research/$FIGURE/dossier.md"
      echo "   Press Enter to continue with outline generation, or Ctrl+C to exit..."
      read
    fi
    echo "📖 Generating book outline..."
    python3 scripts/generate_outline.py "$FIGURE"
    ;;
  batch)
    echo "📊 Running Batch Research for $CSV_FILE ..."
    python3 scripts/run_research_script.py "$CSV_FILE" "research/batch"
    ;;
  enhanced)
    echo "🚀 Running Enhanced Exhaustive Research for $FIGURE ..."
    # Enhanced research = web research + LinkedIn enhancement
    python3 scripts/web_research.py "$FIGURE" $(echo "$OPTIONS" | grep -o '\--[^ ]*')
    LINKEDIN=$(echo "$OPTIONS" | grep -oP '--linkedin="\K[^"]*' || echo "")
    if [ -n "$LINKEDIN" ]; then
      echo "🔗 Enhancing with LinkedIn data..."
      python3 scripts/linkedin_enhance.py "$FIGURE" "$LINKEDIN"
    fi
    ;;
  ultimate)
    echo "🌟 Running Ultimate Exhaustive Research for $FIGURE ..."
    # Ultimate research = web research + LinkedIn + email enrichment
    LINKEDIN=$(echo "$OPTIONS" | grep -oP '--linkedin="\K[^"]*' || echo "")
    EMAIL=$(echo "$OPTIONS" | grep -oP '--email="\K[^"]*' || echo "")
    REFRESH_FLAG=""
    if [[ "$OPTIONS" == *"--refresh"* ]]; then
      REFRESH_FLAG="--refresh"
    fi
    python3 scripts/comprehensive_research.py "$FIGURE" $REFRESH_FLAG \
      $(if [ -n "$LINKEDIN" ]; then echo "--linkedin=\"$LINKEDIN\""; fi) \
      $(if [ -n "$EMAIL" ]; then echo "--email=\"$EMAIL\""; fi)
    ;;
  enrich)
    echo "📧 Running Email Enrichment for $EMAIL_ADDRESS ..."
    python3 scripts/enrich_email.py "$EMAIL_ADDRESS"
    ;;
  expand)
    echo "📝 Expanding chapter for $FIGURE ..."
    CHAPTER=$(echo "$OPTIONS" | grep -oP '--chapter="\K[^"]*' || echo "")
    if [ -z "$CHAPTER" ]; then
      echo "❌ Usage: ./scripts/run_outline.sh expand \"$FIGURE\" --chapter=\"Chapter Title\""
      exit 1
    fi
    python3 scripts/expand_chapter.py "$FIGURE" "$CHAPTER"
    ;;
  expand-all)
    echo "📚 Expanding all chapters for $FIGURE ..."
    python3 scripts/expand_all_chapters.py "$FIGURE"
    ;;
  compile)
    echo "📖 Compiling manuscript for $FIGURE ..."
    python3 scripts/compile_manuscript.py "$FIGURE"
    ;;
  exhaustive)
    echo "🔬 Running Exhaustive Research for $FIGURE ..."
    python3 scripts/exhaustive_research.py "$FIGURE" $(echo "$OPTIONS" | grep -o '\--[^ ]*')
    ;;
  *)
    echo "❌ Unknown workflow: $WORKFLOW"
    echo "Valid options: research | exhaustive | auto | confirm | batch | enhanced | ultimate | enrich | expand | expand-all | compile"
    exit 1
    ;;
esac
