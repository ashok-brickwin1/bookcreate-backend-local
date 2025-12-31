from sqlalchemy.orm import Session
from app.models.question import Answer
from app.schemas.answers import AnswerCreate
from uuid import UUID
import logging, secrets, string
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upsert_answer(db: Session, data: AnswerCreate, book_user_id:UUID) -> Answer:
    """
    Insert or update answer for a given book_user + question_id
    """

    logger.info(f"upserting answer with payload:{data} having book_user_id:{book_user_id}")

    
    answer = (
        db.query(Answer)
        .filter(
            Answer.book_user_id == book_user_id,
            Answer.dummy_question_id == data.dummy_question_id,
        )
        .first()
    )
    payload = data.model_dump(exclude={"book_user_id"})

    if answer:
        logger.info("answer already exists, updating")
        for field, value in payload.items():
            setattr(answer, field, value)

    else:
        logger.info("creating answer")
        answer = Answer(
            book_user_id=book_user_id,  # ✅ server-owned
            **payload
        )
        db.add(answer)

    db.commit()
    db.refresh(answer)
    return answer
