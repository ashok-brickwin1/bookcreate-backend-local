import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class InfluenceType(Base):

    """INFLUENCED TYPES WE SHOW AT THE VERY FIRST PAGE UNDER THE CONTENT THAT CHANGED YOUR LIFE """

    __tablename__ = "influence_type"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentType(Base):
    """TYPES OF CONTENT WE SHOW IN DROPDWON WHILE ANSWERING 
    INFLUENCE QUESTION , THESE ARE LIKE BOOK, MOVIE AND PODCAST ETC"""

    __tablename__ = "content_type"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)







class InfluencingQuestion(Base):

    """THESE ARE THE QUESTIONS WE ASK ON THE VERY FIRST 
    PAGE AS CONTENT THAT CHANGED YOUR LIFE"""
    __tablename__ = "influencing_questions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)
    influence_type_id = Column(UUID(as_uuid=True), ForeignKey("influence_type.id"), nullable=True)
    influence_type = Column(Text,nullable=True)
    content_type = Column(Text,nullable=True)
    title = Column(String(255), nullable=True)
    content_type_id = Column(UUID(as_uuid=True), ForeignKey("content_type.id"), nullable=True)
    life_impact = Column(Text,nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
