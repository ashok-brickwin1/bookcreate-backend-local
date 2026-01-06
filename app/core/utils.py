import secrets
import datetime



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional
from app.models import BookUser, Answer, LifeMoment
from app.api.deps import get_db, get_current_user
from fastapi import Depends, HTTPException
from pathlib import Path
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
import re

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path



logger = logging.getLogger(__name__)

GMAIL_USER = "jagrawal@educatedc.com"  # replace with your email
GMAIL_APP_PASSWORD = "enkn hgvb dfgf ndvq"  # replace with your App Password


# def send_email(to_email: str, subject: str, body: str):
#     """
#     Sends an email using Gmail SMTP with an app password.
#     """
#     logger.info(f"Preparing to send email to {to_email} with subject '{subject}'")
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = GMAIL_USER
#         msg["To"] = to_email
#         msg["Subject"] = subject

#         msg.attach(MIMEText(body, "plain"))

#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
#             # server.send_message(msg)
#             server.sendmail(GMAIL_USER, [to_email], msg.as_string())

#         logger.info(f"Email successfully sent to {to_email}")
#         return True

#     except Exception as e:
#         logger.error(f"Failed to send email to {to_email}: {e}")
#         return False


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path


def send_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_path: Path | None = None,
):
    """
    Sends an email using Gmail SMTP with optional PDF attachment.
    """
    logger.info(f"📧 Preparing to send email to {to_email} | subject='{subject}'")

    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        # 1️⃣ Email body
        msg.attach(MIMEText(body, "plain"))

        # 2️⃣ Attach PDF if provided
        if pdf_path:
            pdf_path = Path(pdf_path)
            logger.info(f"pdf_path at send email:{pdf_path}")

            if not pdf_path.exists():
                logger.info("pdf path does not exist at send email")
                raise FileNotFoundError(f"PDF not found at {pdf_path}")

            with open(pdf_path, "rb") as f:
                pdf_part = MIMEApplication(f.read(), _subtype="pdf")

            pdf_part.add_header(
                "Content-Disposition",
                "attachment",
                filename=pdf_path.name,
            )

            msg.attach(pdf_part)
            logger.info(f"📎 Attached PDF: {pdf_path.name}")

        # 3️⃣ Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        logger.info(f"✅ Email successfully sent to {to_email}")
        return True

    except Exception as e:
        logger.exception(f"❌ Failed to send email to {to_email}")
        return False







def generate_token(nbytes: int = 32):
    return secrets.token_urlsafe(nbytes)

def utcnow():
    return datetime.datetime.utcnow()








def build_user_story_context(
    db: Session,
    book_user_id:UUID
) -> str:
    """
    Builds a rich narrative string from user's answers + life moments
    to be used as prompt context for OpenAI.
    """

    try:



        # 1️⃣ Get latest BookUser
        # book_user: Optional[BookUser] = (
        #     db.query(BookUser)
        #     .filter(
        #         BookUser.user_id == current_user.id,
        #         BookUser.is_deleted == False
        #     )
        #     .order_by(BookUser.created_at.desc())
        #     .first()
        # )

        # if not book_user:
        #     raise HTTPException(status_code=404, detail="Book user not found")

        # 2️⃣ Fetch answers (ordered for coherence)


        logger.info("build_user_story_context called")
        answers = (
            db.query(Answer)
            .filter(Answer.book_user_id == book_user_id)
            .order_by(
                Answer.life_stage.asc(),
                Answer.sub_section.asc(),
                Answer.created_at.asc()
            )
            .all()
        )

        # 3️⃣ Fetch life moments
        life_moments = (
            db.query(LifeMoment)
            .filter(LifeMoment.book_user_id == book_user_id)
            .order_by(LifeMoment.year.asc().nullslast())
            .all()
        )

        # 4️⃣ Build narrative string
        sections: list[str] = []

        sections.append(
            "The following is a detailed personal narrative shared by the user. "
            "It includes reflections, life experiences, formative moments, and lessons learned.\n"
        )

        # -------------------------
        # ANSWERS SECTION
        # -------------------------
        sections.append("### Personal Reflections & Responses\n")

        current_stage = None
        current_section = None

        for ans in answers:
            if ans.life_stage != current_stage:
                current_stage = ans.life_stage
                sections.append(f"\n## Life Stage: {current_stage.title()}\n")

            if ans.sub_section != current_section:
                current_section = ans.sub_section
                sections.append(f"\n### {current_section}\n")

            sections.append(
                f"- **{ans.title}**\n"
                f"  {ans.answer_text.strip()}\n"
            )

        # -------------------------
        # LIFE MOMENTS SECTION
        # -------------------------
        if life_moments:
            sections.append("\n### Significant Life Moments\n")

            for lm in life_moments:
                moment_header = (
                    f"- **{lm.moment_type.upper()} POINT**"
                    f"{f' ({lm.year})' if lm.year else ''}"
                    f" — {lm.life_stage.title()}\n"
                )

                moment_body = []

                if lm.what_happened:
                    moment_body.append(f"  What happened: {lm.what_happened}")

                if lm.story:
                    moment_body.append(f"  Story: {lm.story}")

                if lm.lesson_learned:
                    moment_body.append(f"  Lesson learned: {lm.lesson_learned}")

                sections.append(moment_header + "\n".join(moment_body) + "\n")

        # -------------------------
        # FINAL STRING
        # -------------------------
        final_context = "\n".join(sections).strip()

        logger.info(f"final context created using Answers and life moments")

        return final_context
    

    except Exception as e:
        logger.info(f"failed to generate build user story context:{str(e)}")




import re
from typing import List, Dict
import re
from typing import List, Dict

def build_chapter_summaries_from_outline(outline: str) -> List[Dict]:
    """
    Convert LLM-generated outline text into frontend-friendly chapter summaries.
    Supports chapter headers like:
      - ## Chapter 1
      - ## Chapter 1: Title here
    And/or fields like **Chapter Title:** ...
    """
    chapters: List[Dict] = []

    # Find all chapter sections including their content until next chapter or end
    # Captures:
    #  group(1) = chapter number
    #  group(2) = optional title after colon
    #  group(3) = chapter body
    pattern = re.compile(
        r"^##\s*Chapter\s+(\d+)(?::\s*(.+))?\s*\n(.*?)(?=^##\s*Chapter\s+\d+|\Z)",
        re.MULTILINE | re.DOTALL
    )

    matches = list(pattern.finditer(outline))
    if not matches:
        # fallback: maybe different header style
        return chapters

    for m in matches:
        chapter_num = m.group(1)
        header_title = (m.group(2) or "").strip()
        body = m.group(3).strip()

        # If outline uses **Chapter Title:** inside body, prefer it
        title_match = re.search(r"\*\*Chapter Title:\*\*\s*(.+)", body)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = header_title if header_title else f"Chapter {chapter_num}"

        # Core Focus (handles **Core Focus (Transformational Concept)** or **Core Focus**)
        core_focus_match = re.search(
            r"\*\*Core Focus.*?\*\*\s*\n(.+?)(?=\n\*\*|\Z)",
            body,
            re.DOTALL
        )
        core_focus = core_focus_match.group(1).strip() if core_focus_match else ""

        # Opening Story (handles **Opening Story (Real Moment or Case Study)** or **Opening Story**)
        opening_story_match = re.search(
            r"\*\*Opening Story.*?\*\*\s*\n(.+?)(?=\n\*\*|\Z)",
            body,
            re.DOTALL
        )
        opening_story = opening_story_match.group(1).strip() if opening_story_match else ""

        # Build summary
        summary_parts = []
        if core_focus:
            summary_parts.append(core_focus)
        if opening_story:
            summary_parts.append(opening_story)

        summary = " ".join(summary_parts)
        summary = re.sub(r"\s+", " ", summary).strip()

        # Strength heuristic
        if len(summary) > 300:
            data_strength = "strong"
        elif len(summary) > 150:
            data_strength = "moderate"
        else:
            data_strength = "weak"

        chapters.append({
            "title": title,
            "summary": summary[:600],
            "dataStrength": data_strength
        })

    return chapters



dummy_outline1="""# Revolutionizing the Future: My Algorithm for Building the Impossible

## Introduction

**Book Title:** Revolutionizing the Future: My Algorithm for Building the Impossible

**Core Focus:** This book dives into the raw, unfiltered principles that have driven me to turn audacious visions into reality— from reusable rockets to electric cars that redefine transportation. It's not about luck or genius; it's about a battle-tested algorithm for questioning everything, deleting the unnecessary, and accelerating toward breakthroughs that advance humanity. If you're tired of mediocre corporate drudgery and want to build something that matters, this is your blueprint. We'll strip away the BS and focus on what actually works in the trenches of innovation.

**Opening Story:** Back in the early days of Tesla, I made a classic mistake with our battery production line. We jumped straight into automating everything, thinking it would solve our speed issues. Instead, it turned into a nightmare—robots failing, processes grinding to a halt, and the whole setup feeling like a scene from a Dilbert cartoon. I had to rip it all out, delete the excess, and rebuild from first principles. That painful lesson crystallized my five-step algorithm, saving us from disaster and propelling Tesla forward.

**1 Big Idea:** The essence of true innovation lies in first-principles thinking—breaking problems down to their fundamental truths, like physics, and rebuilding from there. This isn't about incremental tweaks; it's about questioning every assumption to eliminate stupidity and create exponential progress.

**1 Direct Quote:** "Make requirements less dumb by questioning them rigorously and assigning personal responsibility."

## Chapter 1

**Chapter Title:** Question Everything: The Foundation of First-Principles Leadership

**Core Focus (Transformational Concept):** The transformational concept here is relentless questioning as the starting point for any endeavor. In a world full of dumb requirements handed down by "smart" people, true leaders must tie every rule to a named individual who's accountable—not some faceless department. This shifts the game from blind acceptance to personal ownership, preventing costly errors and fostering a culture where innovation thrives on truth, not tradition.

**Opening Story:** Consider my early pitch for SpaceX: I talked about sending a turtle to Mars as a way to capture the absurdity and ambition of making life multi-planetary. People thought it was crazy, but by questioning the status quo of single-use rockets, we deleted the waste and optimized for reusability. This wasn't just talk; it led to the Falcon 9's first successful landing, proving that what NASA deemed impossible could be done cheaper and faster through rigorous scrutiny.

**1 Big Idea:** A maniacal sense of urgency is non-negotiable—time is the ultimate scarce resource, and long timelines are a sign something's inherently wrong. By demanding ultra-hardcore commitment and prioritizing mission over comfort, you force breakthroughs that ordinary efforts can't achieve.

**1 Direct Quote:** "The best part is no part."

## Chapter 2

**Chapter Title:** Delete and Simplify: Cutting the Crap to Accelerate Progress

**Core Focus (Transformational Concept):** The real power comes from aggressive deletion—removing parts, processes, and complexity before you even think about optimizing or automating. This concept transforms bloated systems into lean machines, reducing mass, failure points, and excuses. It's about embracing the mantra that simplicity is the ultimate sophistication, ensuring your efforts focus on what truly advances the mission, whether it's colonizing Mars or electrifying the grid.

**Opening Story:** At Tesla, we once over-automated our battery assembly too soon, leading to a mess where we had to delete entire sections of the line. I remember walking the factory floor myself—going straight to the "red light" problems instead of delegating. We slashed unnecessary steps, simplified the flow, and only then accelerated. This hands-on deletion not only fixed production but inspired the team to push harder, turning a potential failure into a scalable success that powers millions of vehicles today.

**1 Big Idea:** Leaders must maintain direct frontline involvement, physically engaging with problems to motivate and solve them in real-time. This hands-on approach, combined with relentless simplification, enables extraordinary outcomes from what might seem like ordinary resources.

**1 Direct Quote:** "Delete parts or processes (aim to add back only 10% or less)."""




dummy_outline_json={
  "book_title": "Atmanirbhar Bharat: Pathways to Self-Reliance and Sustainability",
  "introduction": {
    "core_focus": "Empowering India through self-reliance, inclusive development, and sustainable practices rooted in traditional knowledge",
    "opening_story": "During my visit to the natural farming summit in Coimbatore, I witnessed farmers integrating ancient wisdom with modern methods for chemical-free cultivation",
    "big_idea": "Combining India's traditional knowledge with ecological principles to address soil degradation and promote self-sufficiency",
    "direct_quote": "integration of India's traditional knowledge with modern ecological principles for chemical-free crop cultivation using farm residues, mulching, and aeration"
  },
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_title": "Natural Farming: Reviving Soil and Communities",
      "core_focus": "Advancing sustainable agriculture through the National Mission on Natural Farming and women's empowerment",
      "opening_story": "At the summit in Coimbatore, I saw hundreds of thousands of farmers adopting practices that reduce chemical dependency and rising costs",
      "big_ideas": [
        "Promoting Shree Anna millets as part of natural farming to enhance food security",
        "Encouraging collective action among farmers, scientists, entrepreneurs, and citizens for soil health"
      ],
      "direct_quotes": [
        "National Mission on Natural Farming launched the previous year, which has connected hundreds of thousands of farmers to sustainable practices",
        "women farmers' growing adoption, addresses challenges like soil degradation from chemical fertilizers and rising costs"
      ]
    },
    {
      "chapter_number": 2,
      "chapter_title": "Self-Reliance and Inclusive Growth: Principles for a New India",
      "core_focus": "Building on natural farming to embody Antyodaya, Swadeshi, and Sabka Saath Sabka Vikas for uplifting the poor and fostering economic independence",
      "opening_story": "From the fields of Coimbatore to national policies, my journey reflects lifting 25 crore people above the poverty line through grassroots schemes",
      "big_ideas": [
        "Prioritizing welfare of the poor via self-reliance and Made in India initiatives",
        "Upholding constitutional values of equality and dignity in harmony with nature and society"
      ],
      "direct_quotes": [
        "Antyodaya and Garib Kalyan (Upliftment of the poorest and welfare of the poor)",
        "Swadeshi and self-reliance (Atmanirbhar Bharat): Promoting economic independence, Made in India"
      ]
    }
  ]
}






def create_book_pdf_from_md(book_dir: str, output_pdf: str):
    """
    Create a single PDF book from markdown chapter files in a directory.
    """

    book_dir = Path(book_dir)
    chapter_files = sorted(book_dir.glob("*.md"))

    if not chapter_files:
        raise ValueError("No chapter files found in book directory")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ChapterTitle",
        fontSize=22,
        leading=28,
        spaceAfter=20,
        alignment=TA_CENTER,
        bold=True
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=15,
        leading=20,
        spaceBefore=18,
        spaceAfter=10,
        bold=True
    ))

    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        fontSize=11,
        leading=16,
        spaceAfter=10
    ))

    story = []

    for chapter_path in chapter_files:
        with open(chapter_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        bullet_buffer = []

        for line in lines:
            line = line.rstrip()

            # Chapter title
            if line.startswith("# "):
                story.append(PageBreak())
                title = line.replace("# ", "")
                story.append(Paragraph(title, styles["ChapterTitle"]))
                story.append(Spacer(1, 0.3 * inch))

            # Section title
            elif line.startswith("## "):
                section = line.replace("## ", "")
                story.append(Spacer(1, 0.2 * inch))
                story.append(Paragraph(section, styles["SectionTitle"]))

            # Bullet point
            elif line.startswith("- "):
                bullet_buffer.append(
                    Paragraph(
                        line.replace("- ", ""),
                        styles["BodyTextCustom"]
                    )
                )

            # Empty line → flush bullets
            elif not line.strip():
                if bullet_buffer:
                    story.append(
                        ListFlowable(
                            bullet_buffer,
                            bulletType="bullet",
                            start="-",
                            leftIndent=20
                        )
                    )
                    bullet_buffer = []
                story.append(Spacer(1, 0.1 * inch))

            # Normal paragraph
            else:
                # Bold markdown → reportlab bold
                line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
                story.append(Paragraph(line, styles["BodyTextCustom"]))

        # Flush remaining bullets
        if bullet_buffer:
            story.append(
                ListFlowable(
                    bullet_buffer,
                    bulletType="bullet",
                    start="bullet",
                    leftIndent=20
                )
            )

    doc.build(story)
