#!/usr/bin/env python3
"""
Compile Manuscript - Replaces Cursor workflow "Compile Manuscript"
Merges all expanded chapters into a single complete manuscript.
"""

import os
import sys
import re
import logging
from pathlib import Path

# Import from expand_chapter module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from expand_chapter import slugify

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def find_chapters(book_dir):
    """Find all chapter files in order."""
    chapters = []
    
    # Look for numbered chapters first (chapter-1-*, chapter-2-*, etc.)
    for i in range(1, 13):
        pattern = f"chapter-{i}-*.md"
        matches = list(book_dir.glob(pattern))
        if matches:
            chapters.append((i, matches[0]))
        else:
            # Try without number prefix
            pattern = f"chapter-{i}*.md"
            matches = list(book_dir.glob(pattern))
            if matches:
                chapters.append((i, matches[0]))
    
    # If we didn't find numbered chapters, try to find any markdown files
    if not chapters:
        all_md = sorted(book_dir.glob("*.md"))
        # Exclude outline and manuscript files
        for md_file in all_md:
            if "outline" not in md_file.name.lower() and "manuscript" not in md_file.name.lower():
                # Try to extract chapter number from filename
                match = re.search(r'chapter[_-]?(\d+)', md_file.name, re.IGNORECASE)
                if match:
                    chapters.append((int(match.group(1)), md_file))
                else:
                    # Add at end if no number found
                    chapters.append((999, md_file))
    
    # Sort by chapter number
    chapters.sort(key=lambda x: x[0])
    
    return [path for _, path in chapters]


def compile_manuscript(figure_name):
    """Compile all chapters into a single manuscript."""
    book_dir = Path("book") / figure_name
    if not book_dir.exists():
        logging.error(f"Book directory not found: {book_dir}")
        return None
    
    # Find all chapters
    chapters = find_chapters(book_dir)
    
    if not chapters:
        logging.error(f"No chapter files found in {book_dir}")
        return None
    
    logging.info(f"Found {len(chapters)} chapters to compile")
    
    # Create manuscript filename
    figure_slug = slugify(figure_name)
    manuscript_path = book_dir / f"{figure_slug}-manuscript.md"
    
    # Check for introduction file
    intro_files = [
        book_dir / "introduction.md",
        book_dir / "intro.md",
        book_dir / "00-introduction.md"
    ]
    intro_content = None
    for intro_file in intro_files:
        if intro_file.exists():
            with open(intro_file, "r", encoding="utf-8") as f:
                intro_content = f.read()
            logging.info(f"Found introduction: {intro_file}")
            break
    
    # Compile manuscript using efficient append operations (like shell >>)
    # This avoids loading the entire manuscript into memory at once
    
    # Start with title page
    with open(manuscript_path, "w", encoding="utf-8") as f:
        f.write(f"# Book Manuscript: {figure_name}\n\n")
        f.write("---\n\n")
    
    # Append introduction if available
    if intro_content:
        with open(manuscript_path, "a", encoding="utf-8") as f:
            f.write(intro_content)
            f.write("\n\n---\n\n")
    
    # Append each chapter efficiently (similar to shell: cat chapter.md >> manuscript.md)
    for i, chapter_path in enumerate(chapters, 1):
        logging.info(f"Adding chapter {i}: {chapter_path.name}")
        
        with open(manuscript_path, "a", encoding="utf-8") as f:
            f.write("\n\n---\n\n")
            
            # Append chapter content (read whole file - chapters are small enough)
            with open(chapter_path, "r", encoding="utf-8") as cf:
                f.write(cf.read())
            
            f.write("\n")
    
    logging.info(f"✅ Manuscript compiled: {manuscript_path}")
    return str(manuscript_path)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Compile all chapters into manuscript")
    parser.add_argument("figure_name", help="Name of the public figure")
    
    args = parser.parse_args()
    
    result = compile_manuscript(args.figure_name)
    
    if result:
        print(f"✅ Manuscript compiled: {result}")
        sys.exit(0)
    else:
        print("❌ Failed to compile manuscript")
        sys.exit(1)


if __name__ == "__main__":
    main()

