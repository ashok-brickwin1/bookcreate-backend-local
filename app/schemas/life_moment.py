from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.base import BaseSchema
from typing import Optional,List


class LifeMomentCreate(BaseModel):
    moment_type: str  # "high" | "low"
    life_stage: str   # foundations | growth | mastery | wisdom
    year: Optional[int] = None
    what_happened: str
    story: Optional[str] = None
    lesson_learned: Optional[str] = None



class LifeMomentBulkCreate(BaseModel):
    moments: List[LifeMomentCreate]


class LifeMomentRead(BaseModel):
    id: UUID
    moment_type: Optional[str]
    life_stage: Optional[str]
    year: Optional[int]
    what_happened: Optional[str]
    story: Optional[str]
    lesson_learned: Optional[str]

    model_config = {
        "from_attributes": True
    }


class LifeMomentUpdate(BaseModel):
    story: str | None = None
    lesson_learned: str | None = None


# class LifeMomentRead(BaseSchema):
#     id: UUID
#     moment_type: str
#     year: int | None
