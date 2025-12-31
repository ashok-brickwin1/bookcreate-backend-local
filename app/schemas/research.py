from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.base import BaseSchema
from typing import Optional


class SourceSiteBase(BaseModel):
    title: str
    description: Optional[str] = None


class SourceSiteCreate(SourceSiteBase):
    pass


class SourceSiteUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class SourceSiteOut(SourceSiteBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class ResearchSourceCreate(BaseModel):
    book_user_id: UUID
    source_site: str | None = None
    source_url: str | None = None


class ResearchSourceUpdate(BaseModel):
    raw_scraped_text: str | None = None
    cleaned_text: str | None = None
    metadata: dict | None = None


class ResearchSourceRead(BaseSchema):
    id: UUID
    source_url: str


class ResearchSourceOut(BaseModel):
    id: UUID
    book_user_id: UUID
    source_site: str | None
    source_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
