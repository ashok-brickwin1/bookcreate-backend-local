from sqlalchemy.orm import Session
from app.models import book_user
from app.models.vision import VisionAnswers
from uuid import UUID
import logging

# root logger
logger = logging.getLogger()
def get_vision_answers_for_book_user(
    db: Session,
    book_user_id,
) -> list:
    rows = (
        db.query(VisionAnswers)
        .filter(VisionAnswers.book_user_id == book_user_id)
        .order_by(VisionAnswers.created_at.asc())
        .all()
    )

    return [
        {
            "vision_question_id": row.question_id,
            "answer": row.text,
        }
        for row in rows
    ]


def upsert_vision_answers(
    db: Session,
    book_user_id: UUID,
    vision_answers: list,
):
    for ans in vision_answers:
        # existing = (
        #     db.query(VisionAnswers)
        #     .filter(
        #         VisionAnswers.book_user_id == book_user_id
        #     )
        #     .first()
        # )

        # # deleting existing and adding new to avoid complexity
        # if existing:
        #     logger.info(f"deleting existing vision answer for book_user_id:{book_user_id} question_id:{ans.vision_question_id}")
        #     db.delete(existing)
        #     db.commit()
        db.query(VisionAnswers).filter(
            VisionAnswers.book_user_id == book_user_id
        ).delete(synchronize_session=False)

        
        
        db.add(
            VisionAnswers(
                book_user_id=book_user_id,
                question_id=ans.vision_question_id,
                text=ans.answer,
            )
        )

    db.commit()
    logger.info(f"upserted vision answers for book_user_id:{book_user_id} answers_count:{len(vision_answers)}")