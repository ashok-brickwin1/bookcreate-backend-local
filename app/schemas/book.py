from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Literal,Optional
from app.schemas.base import BaseSchema


# class BookCreate(BaseModel):
#     book_user_id: UUID
#     book_type_id: UUID
#     style_id: UUID
#     title: str | None = None
#     dedication: str | None = None
#     length_type: Literal["short", "medium", "large"] | None = None


class BookCreate(BaseModel):
    book_user_id: UUID
    genre: Optional[str] = None
    title: Optional[str] = None
    dedication: Optional[str] = None
    number_of_chapters: Optional[int] = None
    length_type: Optional[str] = None  # short | medium | large


class BookSetupSubmitSchema(BaseModel):
    genre: str
    custom_genre: Optional[str] = None
    working_title: str
    chapter_count: int
    desired_length: str
    dedication: Optional[str] = None
    gdpr_consent: bool


class BookSetupRequest(BaseModel):
    book_setup: BookSetupSubmitSchema



class BookUpdate(BaseModel):
    title: str | None = None
    genre: Optional[str] = None
    dedication: str | None = None
    number_of_chapters: Optional[int] = None
    length_type: Optional[str] = None  # short | medium | large
    raw_outline_json: dict | None = None
    raw_book_data: dict | None = None
    status: str | None = None


class BookRead(BaseSchema):
    id: UUID
    book_user_id: UUID
    title: str | None
    status: str
    number_of_chapters: int | None
    created_at: datetime


class BookListSchema(BaseModel):
    id: UUID
    genre: Optional[str] = None
    custom_genre: Optional[str] = None
    working_title: str
    chapter_count: int
    desired_length: Optional[str] = None
    dedication: Optional[str] = None
    gdpr_consent: bool