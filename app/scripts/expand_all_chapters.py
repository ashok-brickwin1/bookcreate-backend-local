#!/usr/bin/env python3
"""
Expand All Chapters - Replaces Cursor workflow "Expand All Chapters"
Expands all chapters from an outline into full manuscript drafts.
"""

import os
import sys
import re
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import from expand_chapter module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from expand_chapter import load_research_archive, expand_chapter, slugify,expand_chapter_copy

load_dotenv()

logger = logging.getLogger()



def extract_chapter_titles_from_outline(outline_content):
    """Extract all chapter titles from the outline."""
    chapters = []
    
    # Primary pattern: Look for "## Chapter N: Title" format
    chapter_pattern = r'(?:^|\n)##\s+Chapter\s+(\d+)[:\.]\s*(.+?)(?=\n|$)'
    matches = re.finditer(chapter_pattern, outline_content, re.MULTILINE | re.IGNORECASE)
    
    chapter_list = []
    for match in matches:
        chapter_num = int(match.group(1))
        chapter_title = match.group(2).strip()
        if chapter_title:
            chapter_list.append((chapter_num, chapter_title))
    
    # Sort by chapter number and extract titles
    chapter_list.sort(key=lambda x: x[0])
    chapters = [title for _, title in chapter_list]
    
    # Fallback: if no chapters found, try alternative patterns
    if not chapters:
        # Try "## Chapter N: Title" without the word "Chapter"
        alt_pattern = r'(?:^|\n)##\s+(\d+)[:\.]\s*(.+?)(?=\n|$)'
        matches = re.finditer(alt_pattern, outline_content, re.MULTILINE)
        for match in matches:
            num = match.group(1)
            title = match.group(2).strip()
            # Only include if it looks like a chapter (has a number 1-20 and substantial title)
            if title and len(title) > 10 and num.isdigit() and 1 <= int(num) <= 20:
                if title not in chapters:
                    chapters.append(title)
    
    logging.info(f"Found {len(chapters)} chapters in outline")
    return chapters


def expand_all_chapters(figure_name):
    """Expand all chapters from the outline."""
    research_dir = Path("research") / figure_name
    book_dir = Path("book") / figure_name
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # Find outline file
    outline_files = [
        research_dir / "outline.md",
        research_dir / f"{figure_name}-book-outline.md",
        book_dir / f"{figure_name}-book-outline.md",
        research_dir / "book-outline.md"
    ]
    
    outline_content = None
    outline_path = None
    for outline_file in outline_files:
        if outline_file.exists():
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_content = f.read()
            outline_path = outline_file
            logging.info(f"Found outline: {outline_path}")
            break
    
    if not outline_content:
        logging.error(f"No outline found for {figure_name}")
        return False
    
    # Extract chapter titles
    chapters = extract_chapter_titles_from_outline(outline_content)
    if not chapters:
        logging.warning("No chapters found in outline. Trying to extract from structure...")
        # Try a different approach - look for any heading that might be a chapter
        lines = outline_content.split('\n')
        for line in lines:
            if line.startswith('##') and 'chapter' in line.lower():
                chapters.append(line.replace('#', '').strip())
    
    if not chapters:
        logging.error("Could not extract chapter titles from outline")
        return False
    
    logging.info(f"Expanding {len(chapters)} chapters...")
    
    # Load research archive
    research_files = load_research_archive(figure_name)
    if not research_files:
        logging.warning(f"No research files found for {figure_name}, proceeding with outline only")
    
    # Add outline to research files for expand_chapter to use
    research_files["outline.md"] = outline_content
    
    # Expand each chapter
    expanded_count = 0
    for i, chapter_title in enumerate(chapters, 1):
        logging.info(f"Expanding chapter {i}/{len(chapters)}: {chapter_title}")
        
        # Check if chapter already exists
        chapter_slug = slugify(chapter_title)
        chapter_path = book_dir / f"{chapter_slug}.md"
        
        if chapter_path.exists():
            logging.warning(f"Chapter already exists: {chapter_path}, skipping...")
            expanded_count += 1
            continue
        
        # Expand chapter
        chapter_content = expand_chapter(figure_name, chapter_title, research_files)
        
        if chapter_content:
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(chapter_content)
            logging.info(f"✅ Chapter {i} saved: {chapter_path}")
            expanded_count += 1
        else:
            logging.error(f"Failed to expand chapter: {chapter_title}")
    
    logging.info(f"✅ Expanded {expanded_count}/{len(chapters)} chapters")
    return expanded_count == len(chapters)


def expand_all_chapters_copy(figure_name,outline):
    """Expand all chapters from the outline."""
    logger.info("expand_all_chapters_copy called")
    logger.info(f"outline in expand all chapters")
    research_dir = Path("static/research") / figure_name
    book_dir = Path("static/book") / figure_name
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # Find outline file
    # outline_files = [
    #     research_dir / "outline.md",
    #     research_dir / f"{figure_name}-book-outline.md",
    #     book_dir / f"{figure_name}-book-outline.md",
    #     research_dir / "book-outline.md"
    # ]
    
    # outline_content = None
    # outline_path = None
    # for outline_file in outline_files:
    #     if outline_file.exists():
    #         with open(outline_file, "r", encoding="utf-8") as f:
    #             outline_content = f.read()
    #         outline_path = outline_file
    #         logging.info(f"Found outline: {outline_path}")
    #         break
    
    if not outline:
        logger.error(f"No outline found for {figure_name}")
        return False
    
    # Extract chapter titles
    chapters = outline["chapters"]
    # chapters= [chapter[chapter_title] for chapter in chapters ]

    logger.info(f"chapters in expand all chapters:{chapters}")
    
    if not chapters:
        logger.error("Could not extract chapter titles from outline")
        return False
    
    logger.info(f"Expanding {len(chapters)} chapters...")
    
    # Load research archive
    research_files = load_research_archive(figure_name) # okay till here 
    if not research_files:
        logger.warning(f"No research files found for {figure_name}, proceeding with outline only")
    
    # Add outline to research files for expand_chapter to use
    # research_files["outline.md"] = outline
    
    # Expand each chapter
    expanded_count = 0
    for i, chapter in enumerate(chapters, start=1):
   
        chapter_title = chapter.get("chapter_title")    

        if i>1:
            prev_summary=chapters[i-1].get("chapter_summary")
        else:
            prev_summary=None

        if not chapter_title:
            logger.warning(f"Chapter {i} missing title, skipping")
            continue

        logger.info(f"Expanding chapter {i}/{len(chapters)}: {chapter_title}")

        chapter_slug = slugify(chapter_title)
        chapter_path = book_dir / f"chapter{i}_{chapter_slug}.md"
        logger.info(f"figure_name:{figure_name}, chapter_title:{chapter_title}, research_files:{research_files},chapter:{chapter}")


        if chapter_path.exists():
            logger.warning(f"Chapter already exists: {chapter_path}, skipping...")
            expanded_count += 1
            continue


        
        chapter_content = expand_chapter_copy(
            figure_name=figure_name,
            chapter_title=chapter_title,
            research_files=research_files,
            chapter=chapter,
            prev_summary=prev_summary
        )

        if chapter_content:
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(chapter_content)

            logger.info(f"✅ Chapter {i} saved: {chapter_path}")
            expanded_count += 1
        else:

            logger.error(f"❌ Failed to expand chapter: {chapter_title}")

    logger.info(f"✅ Expanded {expanded_count}/{len(chapters)} chapters")
    return expanded_count == len(chapters)



def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Expand all chapters from outline")
    parser.add_argument("figure_name", help="Name of the public figure")
    
    args = parser.parse_args()
    
    success = expand_all_chapters(args.figure_name)
    
    if success:
        print(f"✅ All chapters expanded for {args.figure_name}")
        sys.exit(0)
    else:
        print("❌ Some chapters failed to expand")
        sys.exit(1)


if __name__ == "__main__":
    main()

