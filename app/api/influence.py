
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db

from app.models.influence import (
    InfluenceType,
    ContentType,
    InfluencingQuestion
)
from app.schemas.influence import (
    InfluenceTypeCreate, InfluenceTypeOut,
    InfluenceTypeUpdate,
    ContentTypeCreate,
    ContentTypeOut,
    ContentTypeUpdate,
    InfluencingQuestionOut
    
    )

router = APIRouter()
@router.post("/type/create", response_model=InfluenceTypeOut)
def create_influence_type(payload: InfluenceTypeCreate, db: Session = Depends(get_db)):
    obj = InfluenceType(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/type/list", response_model=list[InfluenceTypeOut])
def list_influence_types(db: Session = Depends(get_db)):
    return db.query(InfluenceType).order_by(InfluenceType.created_at.desc()).all()


@router.put("/type/update/{id}", response_model=InfluenceTypeOut)
def update_influence_type(id: UUID, payload: InfluenceTypeUpdate, db: Session = Depends(get_db)):
    obj = db.get(InfluenceType, id)
    if not obj:
        raise HTTPException(404, "Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/type/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_influence_type(id: UUID, db: Session = Depends(get_db)):
    obj = db.get(InfluenceType, id)
    if not obj:
        raise HTTPException(404, "Not found")

    db.delete(obj)
    db.commit()


@router.post("/content-type/create", response_model=ContentTypeOut)
def create_content_type(payload: ContentTypeCreate, db: Session = Depends(get_db)):
    obj = ContentType(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/content-type/list", response_model=list[ContentTypeOut])
def list_content_types(db: Session = Depends(get_db)):
    return db.query(ContentType).order_by(ContentType.created_at.desc()).all()


@router.put("/content-type/update/{id}", response_model=ContentTypeOut)
def update_content_type(id: UUID, payload: ContentTypeUpdate, db: Session = Depends(get_db)):
    obj = db.get(ContentType, id)
    if not obj:
        raise HTTPException(404, "Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/content-type/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content_type(id: UUID, db: Session = Depends(get_db)):
    obj = db.get(ContentType, id)
    if not obj:
        raise HTTPException(404, "Not found")

    db.delete(obj)
    db.commit()


@router.get("/questions/list/all", response_model=list[InfluencingQuestionOut])
def list_influencing_questions(
    db: Session = Depends(get_db),
):
    return (
        db.query(InfluencingQuestion)
        .order_by(InfluencingQuestion.created_at.desc())
        .all()
    )

@router.get("/questions/list/{book_user_id}", response_model=list[InfluencingQuestionOut])
def list_influencing_questions(
    book_user_id: UUID,
    db: Session = Depends(get_db),
):
    return (
        db.query(InfluencingQuestion)
        .filter(InfluencingQuestion.book_user_id == book_user_id)
        .order_by(InfluencingQuestion.created_at.desc())
        .all()
    )


