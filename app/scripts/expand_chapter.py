#!/usr/bin/env python3
"""
Chapter Expander - Replaces Cursor workflow chapter expansion
Expands a single chapter from outline into a full manuscript draft.
"""

import os
import sys
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

logger = logging.getLogger()


def load_research_archive(figure_name):
    """Load all research files in priority order."""
    research_dir = Path("static/research") / figure_name
    if not research_dir.exists():
        return {}
    
    files = {}
    priority_order = [
        "interview.txt",
        "book-outline.md",
        f"{figure_name}-book-outline.md",
        "themes.md",
        "quotes.md",
        "media.md",
        "bio.md",
        "frameworks.md",
        "dossier.md"
    ]
    
    for filename in priority_order:
        filepath = research_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                files[filename] = f.read()
    
    return files


def extract_chapter_from_outline(outline_content, chapter_title):
    """Extract chapter details from outline."""
    # Try to find the chapter in the outline
    pattern = rf"(?i)(?:^|\n)#+\s*{re.escape(chapter_title)}.*?(?=\n#+\s*(?:Chapter|Introduction|$)|\Z)"
    match = re.search(pattern, outline_content, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(0)
    return None


def expand_chapter(figure_name, chapter_title, research_files):
    """Expand a chapter into full manuscript using ChatGPT."""
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set. Cannot expand chapter.")
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        return None
    
    # Find outline
    outline_content = None
    for key in ["book-outline.md", f"{figure_name}-book-outline.md"]:
        if key in research_files:
            outline_content = research_files[key]
            break
    
    if not outline_content:
        logger.error("No outline found in research files")
        return None
    
    # Extract chapter details from outline
    chapter_details = extract_chapter_from_outline(outline_content, chapter_title)
    if not chapter_details:
        logger.warning(f"Chapter '{chapter_title}' not found in outline, proceeding with title only")
        chapter_details = f"# {chapter_title}\n\n[Chapter details from outline not found]"
    
    # Build context
    context_parts = [f"=== CHAPTER TO EXPAND ===\n{chapter_details}\n"]
    
    # Add research files in priority order
    for filename in ["interview.txt", "themes.md", "quotes.md", "media.md", "bio.md", "frameworks.md", "dossier.md"]:
        if filename in research_files:
            context_parts.append(f"=== {filename.upper().replace('.', ' ')} ===\n{research_files[filename]}\n")
    
    full_context = "\n".join(context_parts)
    
    # Truncate if too long (gpt-4o supports ~128k tokens, so ~500k characters is safe)
    MAX_CONTEXT = 500000
    if len(full_context) > MAX_CONTEXT:
        logger.warning(f"Context too long ({len(full_context)} chars), truncating to {MAX_CONTEXT}")
        full_context = full_context[:MAX_CONTEXT] + "\n\n[Context truncated...]"
    
    system_prompt = """You are a professional nonfiction ghostwriter. You expand book outlines into clear, authoritative manuscript chapters written in the first person from the subject's perspective."""
    
    MIN_WORD_COUNT = 3800
    TARGET_WORD_COUNT = 4200
    MAX_ATTEMPTS = 5
    
    # Initial prompt
    user_prompt = f"""Expand the following chapter from the book outline for {figure_name} into a full manuscript chapter written in first person.

**Chapter to Expand:**
{chapter_details}

**Research Archive:**
{full_context}

**Requirements:**
- Target 4,200-4,800 words (absolute minimum 3,800 words)
- Write entirely in first person (I, me, my, we, our)
- Structure:
  - `# {chapter_title}`
  - Opening section: Brief professional introduction to the chapter topic (2-3 paragraphs)
  - Five `##` sections expanding the Big Ideas (use clear, descriptive titles, not "Big Idea 1")
  - Each Big Idea section must include:
    - Professional example or case study from my experience
    - Clear explanation of the concept and its application
    - `**Field Application:**` practical guidance (3-5 bullet points)
    - `**Reflection:**` brief summary paragraph
  - Conclude with `## Synthesis & Next Moves` (synthesize key points, provide 3 actionable steps)
- Integrate at least 6 distinct direct quotes with proper attribution: "Quote." — Source, Publication (Year)
- Use professional, clear language throughout
- Ground insights in specific examples, data, or decisions from my career
- Maintain a professional, authoritative tone consistent with {figure_name}'s voice

**Manuscript Chapter:**
"""
    
    chapter = None
    word_count = 0
    attempt = 0
    
    try:
        while word_count < MIN_WORD_COUNT and attempt < MAX_ATTEMPTS:
            attempt += 1
            
            if attempt == 1:
                # First attempt: generate full chapter
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                max_completion_tokens = 6000
            else:
                # Subsequent attempts: expand existing chapter
                logging.info(f"Chapter too short ({word_count} words), expanding (attempt {attempt})...")
                
                # Identify which sections need expansion
                section_analysis = "Review the chapter and identify sections that need more depth. Focus on:"
                section_analysis += "\n- Adding more detailed examples and case studies"
                section_analysis += "\n- Expanding explanations with additional context"
                section_analysis += "\n- Adding more specific data points or metrics"
                section_analysis += "\n- Deepening the Field Application sections"
                section_analysis += "\n- Expanding the Reflection paragraphs"
                section_analysis += "\n- Adding more quotes where appropriate"
                
                words_needed = MIN_WORD_COUNT - word_count
                expand_prompt = f"""The following chapter is too short ({word_count} words, need minimum {MIN_WORD_COUNT} words). You need to add approximately {words_needed} more words.

**Current Chapter:**
{chapter}

**Research Archive:**
{full_context}

**CRITICAL TASK:**
You must expand this chapter to reach at least {MIN_WORD_COUNT} words. This is not optional. The chapter is currently {word_count} words and needs {words_needed} more words.

**Expansion Strategy:**
1. For each existing section, add 200-400 words by:
   - Adding 2-3 more detailed examples or case studies from the research
   - Expanding explanations with specific data points, metrics, or outcomes
   - Adding more context about implementation challenges and solutions
   - Including additional quotes from the research archive

2. Expand Field Application sections:
   - Add 2-3 more bullet points with specific, actionable guidance
   - Include implementation timelines or considerations
   - Add examples of how to measure success

3. Expand Reflection paragraphs:
   - Add 100-150 words of deeper analysis
   - Connect to broader themes or implications
   - Include lessons learned or key takeaways

4. Add new content where appropriate:
   - Additional subsections if needed
   - More quotes with proper attribution
   - Additional data points or statistics from research

**Requirements:**
- DO NOT repeat existing content
- DO NOT use filler words or padding
- DO add substantive, valuable content
- DO maintain the same professional tone and structure
- DO keep all existing content exactly as written
- DO integrate new content seamlessly
- The final chapter MUST be at least {MIN_WORD_COUNT} words

**Expanded Chapter (must be at least {MIN_WORD_COUNT} words):**
"""
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": chapter},
                    {"role": "user", "content": expand_prompt}
                ]
                max_completion_tokens = 16000  # Increased tokens for substantial expansion
            
            completion = client.chat.completions.create(
                model="gpt-5.1",
                messages=messages,
                temperature=0.7,
                max_completion_tokens=max_completion_tokens
            )
            
            chapter = completion.choices[0].message.content.strip()
            word_count = len(chapter.split())
            logging.info(f"Chapter expanded (attempt {attempt}): {word_count} words")
            
            if word_count >= MIN_WORD_COUNT:
                logging.info(f"✅ Chapter meets minimum word count requirement ({word_count} words)")
                break
            elif attempt >= MAX_ATTEMPTS:
                logging.warning(f"⚠️ Chapter still below minimum after {MAX_ATTEMPTS} attempts ({word_count} words, minimum {MIN_WORD_COUNT})")
        
        return chapter
        
    except Exception as e:
        logging.error(f"Failed to expand chapter: {e}")
        return None

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model


def expand_chapter_copy(figure_name, chapter_title, research_files,chapter,prev_summary=None):
    """Expand a chapter into full manuscript using ChatGPT."""

    logger.info("expand chapter copy called")
    logger.info(f"figure_name:{figure_name},chapter_title{chapter_title}, research_files:{research_files} ,chapter:{chapter}")
    if not OPENAI_API_KEY:
        logging.error("OPENAI_API_KEY not set. Cannot expand chapter.")
        return None
    
    try:
        # client = OpenAI(api_key=OPENAI_API_KEY)
        model = init_chat_model( model="gpt-5.1", api_key=OPENAI_API_KEY, temperature=0.7, max_tokens=1000 )
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        return None
    
    # Find outline
    # outline_content = outline
    # for key in ["book-outline.md", f"{figure_name}-book-outline.md"]:
    #     if key in research_files:
    #         outline_content = research_files[key]
    #         break
    
    # if not outline_content:
    #     logging.error("No outline provided")
    #     return None
    
    # Extract chapter details from outline
    # chapter_details = extract_chapter_from_outline(outline_content, chapter_title)
    chapter_details=chapter
    if not chapter_details:
        logger.warning(f"Chapter '{chapter_title}' not found in outline, proceeding with title only")
        chapter_details = f"# {chapter_title}\n\n[Chapter details from outline not found]"
    
    # Build context
    context_parts = [f"=== CHAPTER TO EXPAND ===\n{chapter_details}\n"]
    
    # Add research files in priority order
    for filename in ["interview.txt", "themes.md", "quotes.md", "media.md", "bio.md", "frameworks.md", "dossier.md"]:
        if filename in research_files:
            context_parts.append(f"=== {filename.upper().replace('.', ' ')} ===\n{research_files[filename]}\n")
    
    full_context = "\n".join(context_parts)

    logger.info(f"full cnotext:{full_context}")
    
    # Truncate if too long (gpt-4o supports ~128k tokens, so ~500k characters is safe)
    MAX_CONTEXT = 500000
    if len(full_context) > MAX_CONTEXT:
        logger.warning(f"Context too long ({len(full_context)} chars), truncating to {MAX_CONTEXT}")

        full_context = full_context[:MAX_CONTEXT] + "\n\n[Context truncated...]"
    
    system_prompt = """You are a professional nonfiction ghostwriter. You expand book outlines into clear, authoritative manuscript chapters written in the first person from the subject's perspective."""
    
    MIN_WORD_COUNT = 3800
    TARGET_WORD_COUNT = 4200
    MAX_ATTEMPTS = 5
    
    # Initial prompt
    user_prompt = f"""Expand the following chapter from the book outline for {figure_name} into a full manuscript chapter written in first person.

**Chapter to Expand:**
{chapter_details}

**Research Archive:**
{full_context}

**Requirements:**
- Target 4,200-4,800 words (absolute minimum 3,800 words)
- Write entirely in first person (I, me, my, we, our)
- Structure:
  - `# {chapter_title}`
  - Opening section: Brief professional introduction to the chapter topic (2-3 paragraphs)
  - Two `##` sections expanding the Big Ideas (use clear, descriptive titles, not "Big Idea 1")
  - Each Big Idea section must include:
    - Professional example or case study from my experience
    - Clear explanation of the concept and its application
    - `**Field Application:**` practical guidance (3-5 bullet points)
    - `**Reflection:**` brief summary paragraph
  - Conclude with `## Synthesis & Next Moves` (synthesize key points, provide 3 actionable steps)
- Integrate at least 6 distinct direct quotes with proper attribution: "Quote." — Source, Publication (Year)
- Use professional, clear language throughout
- Ground insights in specific examples, data, or decisions from my career
- Maintain a professional, authoritative tone consistent with {figure_name}'s voice

**Manuscript Chapter:**
"""
    
    chapter = None
    word_count = 0
    attempt = 0
    
    try:
        while word_count < MIN_WORD_COUNT and attempt < MAX_ATTEMPTS:
            attempt += 1
            
            if attempt == 1:
                # First attempt: generate full chapter
                logger.info("first attempt")
                # messages = [
                #     {"role": "system", "content": system_prompt},
                #     {"role": "user", "content": user_prompt}
                # ]
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
                max_completion_tokens = 6000
            else:
                # Subsequent attempts: expand existing chapter
                logger.info(f"Chapter too short ({word_count} words), expanding (attempt {attempt})...")
                
                # Identify which sections need expansion
                section_analysis = "Review the chapter and identify sections that need more depth. Focus on:"
                section_analysis += "\n- Adding more detailed examples and case studies"
                section_analysis += "\n- Expanding explanations with additional context"
                section_analysis += "\n- Adding more specific data points or metrics"
                section_analysis += "\n- Deepening the Field Application sections"
                section_analysis += "\n- Expanding the Reflection paragraphs"
                section_analysis += "\n- Adding more quotes where appropriate"
                
                words_needed = MIN_WORD_COUNT - word_count
                expand_prompt = f"""The following chapter is too short ({word_count} words, need minimum {MIN_WORD_COUNT} words). You need to add approximately {words_needed} more words.

**Current Chapter:**
{chapter}

**Previous Summary:** 
{prev_summary}

**Research Archive:**
{full_context}

**CRITICAL TASK:**
You must expand this chapter to reach at least {MIN_WORD_COUNT} words. This is not optional. The chapter is currently {word_count} words and needs {words_needed} more words.

**Expansion Strategy:**
1. For each existing section, add 200-400 words by:
   - Adding 2-3 more detailed examples or case studies from the research
   - Expanding explanations with specific data points, metrics, or outcomes
   - Adding more context about implementation challenges and solutions
   - Including additional quotes from the research archive

2. Expand Field Application sections:
   - Add 2-3 more bullet points with specific, actionable guidance
   - Include implementation timelines or considerations
   - Add examples of how to measure success




**Requirements:**
- DO NOT repeat existing content
- DO NOT use filler words or padding
- DO add substantive, valuable content
- DO maintain the same professional tone and structure
- DO keep all existing content exactly as written
- DO integrate new content seamlessly
- The final chapter MUST be at least {MIN_WORD_COUNT} words

**Expanded Chapter (must be at least {MIN_WORD_COUNT} words):**
"""
                
                messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt),
                        AIMessage(content=chapter),
                        HumanMessage(content=expand_prompt),
                    ]

                max_completion_tokens = 16000  # Increased tokens for substantial expansion
            
            response = model.invoke(messages)
            
            chapter = response.content.strip()
            word_count = len(chapter.split())
            logger.info(f"Chapter expanded (attempt {attempt}): {word_count} words")
            
            if word_count >= MIN_WORD_COUNT:
                logger.info(f"✅ Chapter meets minimum word count requirement ({word_count} words)")
                break
            elif attempt >= MAX_ATTEMPTS:
                logger.warning(f"⚠️ Chapter still below minimum after {MAX_ATTEMPTS} attempts ({word_count} words, minimum {MIN_WORD_COUNT})")
        
        return chapter
        
    except Exception as e:
        logger.error(f"Failed to expand chapter: {e}")
        return None


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Expand a chapter from outline")
    parser.add_argument("figure_name", help="Name of the public figure")
    parser.add_argument("chapter_title", help="Title of the chapter to expand")
    
    args = parser.parse_args()
    
    # Load research files
    research_files = load_research_archive(args.figure_name)
    if not research_files:
        logging.error(f"No research files found for {args.figure_name}")
        sys.exit(1)
    
    # Expand chapter
    logging.info(f"Expanding chapter '{args.chapter_title}' for {args.figure_name}...")
    chapter = expand_chapter(args.figure_name, args.chapter_title, research_files)
    
    if chapter:
        # Save chapter
        book_dir = Path("book") / args.figure_name
        book_dir.mkdir(parents=True, exist_ok=True)
        
        chapter_slug = slugify(args.chapter_title)
        chapter_path = book_dir / f"{chapter_slug}.md"
        
        with open(chapter_path, "w", encoding="utf-8") as f:
            f.write(chapter)
        
        logging.info(f"✅ Chapter saved to {chapter_path}")
        print(f"✅ Chapter expanded: {chapter_path}")
        sys.exit(0)
    else:
        logging.error("Failed to expand chapter")
        sys.exit(1)


if __name__ == "__main__":
    main()
