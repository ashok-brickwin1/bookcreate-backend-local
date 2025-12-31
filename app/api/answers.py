from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.book_user import BookUser
from app.schemas.answers import AnswerCreate, AnswerBulkSubmit
from app.crud.answers import upsert_answer
import logging, secrets, string
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/save")
def save_answer(
    payload: AnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate ownership
    logger.info(f"Payload at save answer:{payload}")

    book_user = (
            db.query(BookUser)
            .filter(
                BookUser.user_id == current_user.id,
                BookUser.is_deleted == False
            )
            .order_by(BookUser.created_at.desc())
            .first()
        )

    
    # book_user = (
    #     db.query(BookUser)
    #     .filter(
    #         BookUser.id == payload.book_user_id,
    #         BookUser.user_id == current_user.id,
    #         BookUser.is_deleted == False
    #     )
    #     .first()
    # )

    if not book_user:
        logger.info("book_user not found")
        raise HTTPException(status_code=403, detail="Unauthorized")

    answer = upsert_answer(db, payload,book_user_id=book_user.id)

    logger.info("answeres saved successfully")

    return {
        "success": True,
        "answer_id": answer.id,
        "message": "Answer saved"
    }



@router.post("/bulk-save")
def bulk_save_answers(
    payload: AnswerBulkSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = []

    for answer_data in payload.answers:
        answer = upsert_answer(db, answer_data)
        saved.append(answer.id)

    return {
        "success": True,
        "saved_count": len(saved),
        "message": "Answers saved successfully"
    }
