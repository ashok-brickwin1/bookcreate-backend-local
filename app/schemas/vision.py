from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class VisionQuestionTypeBase(BaseModel):
    title: str


class VisionQuestionTypeCreate(VisionQuestionTypeBase):
    pass


class VisionQuestionTypeUpdate(BaseModel):
    title: Optional[str] = None


class VisionQuestionTypeOut(VisionQuestionTypeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True






class VisionQuestionBase(BaseModel):
    text: str
    vision_type_id: UUID
    vision_type_title: str


class VisionQuestionCreate(VisionQuestionBase):
    pass


class VisionQuestionUpdate(BaseModel):
    text: Optional[str] = None
    vision_type_id: Optional[UUID] = None


class VisionQuestionOut(VisionQuestionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class VisionAnswerOut(BaseModel):
    id: UUID
    question_id: UUID
    book_user_id: UUID
    text: str | None
    created_at: datetime

    class Config:
        from_attributes = True
