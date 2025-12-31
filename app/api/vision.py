from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.models.vision import VisionQuestionType
from app.schemas.vision import (
    VisionQuestionTypeCreate,
    VisionQuestionTypeUpdate,
    VisionQuestionTypeOut,
    VisionAnswerOut
)
from app.models.vision import VisionQuestion, VisionQuestionType,VisionAnswers
from app.schemas.vision import (
    VisionQuestionCreate,
    VisionQuestionUpdate,
    VisionQuestionOut,
)

router = APIRouter()


@router.post("/type/create", response_model=VisionQuestionTypeOut, status_code=status.HTTP_201_CREATED)
def create_vision_question_type(
    payload: VisionQuestionTypeCreate, db: Session = Depends(get_db)
):
    item = VisionQuestionType(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/type/list", response_model=list[VisionQuestionTypeOut])
def list_vision_question_types(db: Session = Depends(get_db)):
    return db.query(VisionQuestionType).order_by(
        VisionQuestionType.created_at.desc()
    ).all()


@router.put("/type/update/{type_id}", response_model=VisionQuestionTypeOut)
def update_vision_question_type(
    type_id: UUID,
    payload: VisionQuestionTypeUpdate,
    db: Session = Depends(get_db),
):
    item = db.query(VisionQuestionType).filter(
        VisionQuestionType.id == type_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Vision question type not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/type/delete/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vision_question_type(type_id: UUID, db: Session = Depends(get_db)):
    item = db.query(VisionQuestionType).filter(
        VisionQuestionType.id == type_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Vision question type not found")

    db.delete(item)
    db.commit()






@router.post("/question/create", response_model=VisionQuestionOut, status_code=status.HTTP_201_CREATED)
def create_vision_question(
    payload: VisionQuestionCreate, db: Session = Depends(get_db)
):
    # FK validation
    if not db.query(VisionQuestionType).filter(
        VisionQuestionType.id == payload.vision_type_id
    ).first():
        raise HTTPException(status_code=400, detail="Invalid vision_type_id")

    question = VisionQuestion(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/question/list", response_model=list[VisionQuestionOut])
def list_vision_questions(db: Session = Depends(get_db)):
    questions = (
        db.query(VisionQuestion)
        .join(VisionQuestion.vision_type)
        .order_by(VisionQuestion.created_at.desc())
        .all()
    )

    return [
        {
            "id": q.id,
            "text": q.text,
            "vision_type_id": q.vision_type_id,
            "vision_type_title": q.vision_type.title,  # ✅ HERE
            "created_at": q.created_at,
            "updated_at": q.updated_at,
        }
        for q in questions
    ]


@router.put("/question/update/{question_id}", response_model=VisionQuestionOut)
def update_vision_question(
    question_id: UUID,
    payload: VisionQuestionUpdate,
    db: Session = Depends(get_db),
):
    question = db.query(VisionQuestion).filter(
        VisionQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Vision question not found")

    if payload.vision_type_id:
        if not db.query(VisionQuestionType).filter(
            VisionQuestionType.id == payload.vision_type_id
        ).first():
            raise HTTPException(status_code=400, detail="Invalid vision_type_id")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question


@router.delete("/question/delete/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vision_question(question_id: UUID, db: Session = Depends(get_db)):
    question = db.query(VisionQuestion).filter(
        VisionQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Vision question not found")

    db.delete(question)
    db.commit()



@router.get("/answer/list/", response_model=list[VisionAnswerOut])
def list_vision_answers(
    db: Session = Depends(get_db),
):
    answers = (
        db.query(VisionAnswers)
        .order_by(VisionAnswers.created_at.desc())
        .all()
    )

    return answers