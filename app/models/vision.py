import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class VisionQuestionType(Base):

    """INFLUENCED TYPES WE SHOW AT THE VERY FIRST PAGE UNDER THE CONTENT THAT CHANGED YOUR LIFE """

    __tablename__ = "vision_question_type"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VisionQuestion(Base):
    "VISION QUESTIONS THAT WILL BE ASKED AT THE VERY FIRST PAGE"

    __tablename__ = "vision_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String(255),nullable=False)
    vision_type_id = Column(UUID(as_uuid=True), ForeignKey("vision_question_type.id"), nullable=False)
    vision_type = relationship("VisionQuestionType")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VisionAnswers(Base):
    "ANSWERS OF VISION QUESTIONS GIVEN BY BOOKUSER"

    __tablename__ = "vision_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("vision_questions.id"), nullable=False)
    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)
    text = Column(String(255),nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

