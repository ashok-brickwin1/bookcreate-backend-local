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


logger = logging.getLogger(__name__)

GMAIL_USER = "passbyteou@gmail.com"  # replace with your email
GMAIL_APP_PASSWORD = "qnpi mktl cmre nibm"  # replace with your App Password


def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using Gmail SMTP with an app password.
    """
    logger.info(f"Preparing to send email to {to_email} with subject '{subject}'")
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            # server.send_message(msg)
            server.sendmail(GMAIL_USER, [to_email], msg.as_string())

        logger.info(f"Email successfully sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
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
  "book_title": "Atmanirbhar Bharat: Self-Reliance Through Sustainable Progress",
  "introduction": {
    "core_focus": "Embracing India's traditional knowledge for modern self-reliance and inclusive growth",
    "opening_story": "During my visit to the natural farming summit in Coimbatore, I witnessed farmers integrating ancient wisdom with contemporary methods to cultivate crops without chemicals",
    "big_idea": "True progress lies in self-reliance, uplifting the poorest, and harmonious development for all through principles like Antyodaya and Sabka Saath Sabka Vikas",
    "direct_quote": "integration of India's traditional knowledge with modern ecological principles for chemical-free crop cultivation using farm residues, mulching, and aeration"
  },
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_title": "Natural Farming: Reviving Soil and Self-Sufficiency",
      "core_focus": "Addressing soil degradation and promoting sustainable agriculture through government initiatives",
      "opening_story": "At the summit in Coimbatore, I saw hundreds of thousands of farmers connected to natural practices, reducing dependency on chemical fertilizers",
      "big_idea": "National Mission on Natural Farming embodies Atmanirbhar Bharat by linking traditional methods to modern challenges like rising costs and environmental stewardship",
      "direct_quote": "National Mission on Natural Farming launched the previous year, which has connected hundreds of thousands of farmers to sustainable practices"
    },
    {
      "chapter_number": 2,
      "chapter_title": "Inclusive Growth: Empowering Women and Communities",
      "core_focus": "Fostering collective action and women's adoption of natural farming for broader welfare",
      "opening_story": "Building on the farming mission, I observed women farmers leading the shift to millets and residue-based cultivation, embodying upliftment of the underprivileged",
      "big_idea": "Sabka Saath Sabka Vikas through Antyodaya means involving farmers, scientists, entrepreneurs, and citizens in self-reliant, inclusive development",
      "direct_quote": "women farmers' growing adoption, addresses challenges like soil degradation from chemical fertilizers and rising costs, and calls for collective action among farmers, scientists, entrepreneurs, and citizens"
    }
  ]
}