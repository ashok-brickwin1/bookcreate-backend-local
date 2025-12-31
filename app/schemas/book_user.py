from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from app.schemas.base import BaseSchema


class   BookUserCreate(BaseModel):
    user_id: UUID
    name: str | None = None
    email: EmailStr
    title: str | None = None
    bio: str | None = None


class BookUserUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    digital_footprint_summary: str | None = None


class BookUserRead(BaseSchema):
    id: UUID
    user_id: UUID
    name: str | None
    email: EmailStr
    title: str | None
    bio: str | None
    digital_footprint_summary: str | None
    created_at: datetime
