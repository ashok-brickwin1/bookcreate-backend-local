# app/schemas/book_setup.py
from pydantic import BaseModel
from typing import Optional


class BookSetupSchema(BaseModel):
    genre: str
    custom_genre: Optional[str] = None
    working_title: str
    chapter_count: int
    desired_length: str
    dedication: Optional[str] = None
    gdpr_consent: bool


class BookSetupSubmitSchema(BaseModel):
    book_setup: BookSetupSchema
