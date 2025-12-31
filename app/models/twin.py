import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base



class Twin(Base):
    "TO SAVE MODEL SELETED FOR TWIN FOR A BOOK USER"
    __tablename__ = "twins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)
    model = Column(String(255),nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


