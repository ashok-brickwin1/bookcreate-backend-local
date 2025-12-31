from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class AnswerCreate(BaseModel):
    dummy_question_id: str

    category: Optional[str] = None
    sub_section: Optional[str] = None
    life_stage: Optional[str] = None

    title: Optional[str] = None
    prompt: Optional[str] = None
    help_text: Optional[str] = None
    context_prompt: Optional[str] = None

    answer_text: Optional[str] = None


class AnswerBulkSubmit(BaseModel):
    answers: list[AnswerCreate]
