import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, String, Integer, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Chapter(Base):
    "WE KEEP DATA FOR CHAPTERS OF BOOK , CREATED WHEN THE OUTLINE IS GENERATED USING AI" 
    __tablename__ = "chapters"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)

    chapter_index = Column(Integer, nullable=False)
    title = Column(String(255),nullable=True)
    description=Column(String(255),nullable=True)

    pages = Column(JSON,nullable=True)
    # Example:
    # {
    #   "sections": [
    #       {"heading": "...", "content": "..."}
    #   ]
    # }

    status = Column(
        Enum("pending", "ready", name="chapter_status"),
        default="pending",nullable=True
    )

    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

