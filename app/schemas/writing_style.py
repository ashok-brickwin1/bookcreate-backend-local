from pydantic import BaseModel
from uuid import UUID
from app.schemas.base import BaseSchema


class StyleCreate(BaseModel):
    name: str
    content_type_id: UUID
    url: str | None = None
    pasted_text: str | None = None


class StyleRead(BaseSchema):
    id: UUID
    name: str
