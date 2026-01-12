import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from sqlalchemy import Boolean


class BookType(Base):
    "BOOK TYPES CAN BE LIKE AUTOBIOGRAPHY, MEMOIR, LEGACY BOOK  ETC"
    __tablename__ = "book_types"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    




class Book(Base):

    """TO KEEP DATA RELATED TO BOOK LIKE NO OF CHAPTERS ,STATUS 
    , STYLE OF BOOK, OUTLINE OF CHAPTERS"""
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)
    style_id = Column(UUID(as_uuid=True), ForeignKey("styles.id"), nullable=True)
    book_type_id = Column(UUID(as_uuid=True), ForeignKey("book_types.id"), nullable=True)
    genre=Column(Text,nullable=True)
    title = Column(String(255), nullable=True)
    dedication = Column(Text,nullable=True)
    number_of_chapters = Column(Integer,nullable=True)
    length_type = Column(
       Text,nullable=True
    )
    status = Column(
        String(255),
        default="draft"
    )
    raw_outline_json=Column(JSON,nullable=True)
    raw_book_data=Column(JSON,nullable=True)
    
    is_deleted = Column(Boolean, default=False)


    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)





