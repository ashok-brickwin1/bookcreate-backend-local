
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.base import BaseSchema
from typing import Optional



class InfluenceTypeCreate(BaseModel):
    title: str

class InfluenceTypeUpdate(BaseModel):
    title: Optional[str] = None

class InfluenceTypeOut(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContentTypeCreate(BaseModel):
    title: str

class ContentTypeUpdate(BaseModel):
    title: Optional[str] = None

class ContentTypeOut(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

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



class InfluencingQuestionOut(BaseModel):
    id: UUID
    book_user_id: UUID
    influence_type: str | None
    content_type: str | None
    title: str | None
    life_impact: str | None
    created_at: datetime

    class Config:
        from_attributes = True