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
