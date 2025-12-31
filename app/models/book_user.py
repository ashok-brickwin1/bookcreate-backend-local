import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from sqlalchemy import Boolean




class BookUser(Base):

    "SAVING DATA FOR THE VERY FIRST PAGE ABOUT CURRENT BOOKUSER ALSO THE DIGITAL FOOTPRINT SUMMARY CREATED"
    __tablename__ = "book_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Identity
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    title = Column(String(255),nullable=True)  
    bio = Column(Text,nullable=True)
    digital_footprint_summary = Column(Text,nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

