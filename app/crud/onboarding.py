from sqlalchemy.orm import Session
from uuid import UUID
import json

from app.models.user import User
from app.models.book_user import BookUser
from app.models.influence import InfluencingQuestion
from app.models.vision import VisionAnswers
from collections import defaultdict
import logging

# root logger
logger = logging.getLogger()




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




def get_influential_content_for_book_user(
    db: Session,
    book_user_id,
) -> dict:
    rows = (
        db.query(InfluencingQuestion)
        .filter(InfluencingQuestion.book_user_id == book_user_id)
        .order_by(InfluencingQuestion.created_at.asc())
        .all()
    )

    influential_content = defaultdict(list)

    for row in rows:
        if not row.influence_type:
            continue

        key = row.influence_type.strip().lower()

        influential_content[key].append({
            "type": row.content_type,
            "title": row.title,
            "why": row.life_impact,
        })

    return dict(influential_content)

#ASHOK ADDED THIS UPDATE AND CREATE INFLUENCE QUESTION
def upsert_influential_content(
    db: Session,
    book_user_id: UUID,
    influential_content: dict,
):
    
    db.query(InfluencingQuestion).filter(
        InfluencingQuestion.book_user_id == book_user_id
    ).delete(synchronize_session=False)

    db.commit()
    
    for influence_type, items in influential_content.items():
        for item in items:
           
            
            db.add(
                InfluencingQuestion(
                    book_user_id=book_user_id,
                    influence_type=influence_type,
                    content_type=item["type"],
                    title=item["title"],
                    life_impact=item["why"],
                )
            )

    db.commit()

    logger.info(f"upserted influential content for book_user_id:{book_user_id} content_types_count:{len(influential_content)}") 