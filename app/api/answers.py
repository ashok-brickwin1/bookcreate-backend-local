from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.book_user import BookUser
from app.models.question import Answer
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








from pydantic import BaseModel
from typing import List



class AnswerItemSchema(BaseModel):
    question_id: str
    answer_text: str


class AnswerListResponseSchema(BaseModel):
    answers: List[AnswerItemSchema]


@router.get(
    "/dummy",
    response_model=AnswerListResponseSchema
)
def get_dummy_answers(current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),):
    """
    Dummy endpoint to prefill guided interview answers
    """
    logger.info("Providing dummy answers for guided interview")
    return {
        "answers": [
            {
                "question_id": "personal-earliest-understanding",
                "answer_text": "I grew up in a close-knit family that valued education and curiosity."
            },
            {
                "question_id": "personal-influential-people",
                "answer_text": "My career started with a deep interest in building things that help people."
            },
            {
                "question_id": "prof-first-career-choice",
                "answer_text": "A major turning point was leaving a stable job to pursue entrepreneurship."
            }
        ]
    }




question_ids = [
    # PERSONAL — Foundations of Self
    "personal-earliest-understanding",
    "personal-influential-people",
    "personal-shaping-stories",
    "personal-defining-setback",

    # PERSONAL — Growth & Change
    "personal-first-realization",
    "personal-struggle-shaped",
    "personal-transitional-influences",
    "personal-mistake-lesson",

    # PERSONAL — Evolving Priorities
    "personal-rethink-priorities",
    "personal-emotional-challenge",
    "personal-philosophy-shift",

    # PERSONAL — Reflection & Wisdom
    "personal-lesson-others",
    "personal-truly-matters",
    "personal-wisdom-younger-self",

    # PROFESSIONAL — Early Career & First Decisions
    "prof-first-career-choice",
    "prof-first-failure",
    "prof-early-mentor",
    "prof-influential-book",

    # PROFESSIONAL — Professional Growth & Leadership
    "prof-major-risk",
    "prof-leadership-challenge",
    "prof-skill-shift",
    "prof-leadership-influence",

    # PROFESSIONAL — Mastery & Industry Impact
    "prof-best-decision",
    "prof-leadership-lesson",
    "prof-hardest-lesson",
    "prof-mentor-advice",

    # CURIOSITY — Recognizing Patterns & Predicting
    "curiosity-patterns",
    "curiosity-unpopular-opinion",

    # CURIOSITY — Refining Expertise & Teaching
    "curiosity-industry-problem",
    "curiosity-changed-mind",
    "curiosity-framework",

    # CURIOSITY — Wisdom & Teaching
    "curiosity-younger-professionals",
    "curiosity-mindset-shift",
    "curiosity-enduring-influences",

    # LEGACY — Defining Your Legacy
    "legacy-first-thinking",
    "legacy-best-advice",
    "legacy-built-to-outlast",

    # LEGACY — Passing Down Wisdom
    "legacy-core-principles",
    "legacy-mistakes-to-avoid",
    "legacy-lessons-to-learn",
    "legacy-ai-phrase",
]


@router.get(
    "/get-user-answers",
    response_model=AnswerListResponseSchema
)
def get_answers(current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),):
    """
    Get answers for guided interview
    """

    try:
            
        logger.info("Providing answers for guided interview")
        book_user = (
                db.query(BookUser)
                .filter(
                    BookUser.user_id == current_user.id,
                    BookUser.is_deleted == False
                )
                .order_by(BookUser.created_at.desc())
                .first()
            )
        
        allanswer = answer = (
                db.query(Answer)
                .filter(
                    Answer.book_user_id == book_user.id
                )
                .order_by(Answer.created_at.desc())
                .all()
            )
        
        logger.info(f"no of answers found:{len(allanswer)}")
        
        answers = []

        for qid in question_ids:
            answer = (
                db.query(Answer)
                .filter(
                    Answer.book_user_id == book_user.id,
                    Answer.dummy_question_id == qid
                )
                .order_by(Answer.created_at.desc())
                .first()
            )
            if answer:
                logger.info(f"found answer for question_id:{qid} answer_text:{answer.answer_text}")
            else:
                logger.info(f"no answer found for question_id:{qid}, returning empty string")
            answers.append(
                AnswerItemSchema(
                    question_id=qid,
                    answer_text=answer.answer_text if answer else ""
                )
            )

        return {
            "answers": answers
        }
    except Exception as e:
        logger.error(f"Error fetching answers: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

        
