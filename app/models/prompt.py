import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    prompt_type = Column(
        Enum("research", "outline", "expand_chapter", name="prompt_type"),
        nullable=False
    )

    default_prompt = Column(Text,nullable=True)
    user_custom_prompt = Column(Text,nullable=True)



    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

