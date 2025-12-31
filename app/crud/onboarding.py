from sqlalchemy.orm import Session
from uuid import UUID
import json

from app.models.user import User
from app.models.book_user import BookUser
from app.models.influence import InfluencingQuestion
from app.models.vision import VisionAnswers




# ---------- INFLUENTIAL CONTENT ----------

def save_influential_content(
    db: Session,
    book_user_id: UUID,
    influential_content: dict,
):
    for influence_type, items in influential_content.items():
        for item in items:
            row = InfluencingQuestion(
                book_user_id=book_user_id,
                influence_type=influence_type,   # personal / professional etc
                content_type=item["type"],       # book / movie etc
                title=item["title"],
                life_impact=item["why"],
            )
            db.add(row)

    db.commit()


# ---------- VISION ANSWERS ----------

def save_vision_answers(
    db: Session,
    book_user_id: UUID,
    vision_answers: list,
):
    for ans in vision_answers:
        row = VisionAnswers(
            question_id=ans.vision_question_id,
            book_user_id=book_user_id,
            text=ans.answer,
        )
        db.add(row)

    db.commit()
