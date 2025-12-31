from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.base import BaseSchema


class ChapterCreate(BaseModel):
    book_id: UUID
    chapter_index: int
    title: str | None = None
    description: str | None = None


class ChapterUpdate(BaseModel):
    pages: dict | None = None
    status: str | None = None


class ChapterRead(BaseSchema):
    id: UUID
    book_id: UUID
    chapter_index: int
    title: str | None
    status: str







class InfluencingQuestionCreate(BaseModel):
    book_user_id: UUID
    influence_type_id: UUID
    content_type_id: UUID
    title: str | None = None
    life_impact: str | None = None


class InfluencingQuestionUpdate(BaseModel):
    title: str | None = None
    life_impact: str | None = None


class InfluencingQuestionRead(BaseSchema):
    id: UUID
    title: str | None
    life_impact: str | None
