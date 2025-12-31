from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.base import BaseSchema
from typing import Optional





class QuestionRead(BaseSchema):
    id: UUID
    question_type_id: UUID
    text: str
    title: str | None


# class AnswerCreate(BaseModel):
#     book_user_id: UUID
#     question_id: UUID
#     answer_text: str


class AnswerUpdate(BaseModel):
    answer_text: str


class AnswerRead(BaseSchema):
    id: UUID
    book_user_id: UUID
    question_id: UUID
    answer_text: str
    created_at: datetime







class QuestionTypeCreate(BaseModel):
    title: str
    description: Optional[str] = None

class QuestionTypeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class QuestionTypeOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]

    class Config:
        from_attributes = True




class QuestionCreate(BaseModel):
    question_type_id: Optional[UUID]
    text: str
    title: Optional[str] = None

class QuestionUpdate(BaseModel):
    question_type_id: Optional[UUID] = None
    text: Optional[str] = None
    title: Optional[str] = None

class QuestionOut(BaseModel):
    id: UUID
    question_type_id: Optional[UUID]
    text: str
    title: Optional[str]

    class Config:
        from_attributes = True





