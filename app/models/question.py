
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base





class QuestionType(Base):
    """TYPE OF QUESTIONS WE HAVE CATEGORIZED IN INTERVIEW LIKE PROFESSIONAL, 
    PERSONAL AND Curiosity & Growth ETC"""
    
    __tablename__ = "question_type"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)






class Question(Base):
    """THESE ARE THE QUESTIONS WE ASK IN INTERVIEW (THOSE 41 QUESTIONS)"""
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_type_id = Column(UUID(as_uuid=True), ForeignKey("question_type.id"), nullable=True)
    text = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class Answer(Base):

    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True
    )
    dummy_question_id = Column(Text,nullable=True)
    category=Column(Text,nullable=True)
    sub_section=Column(Text,nullable=True)
    life_stage=Column(Text,nullable=True)
    title=Column(Text,nullable=True)
    prompt=Column(Text,nullable=True)
    help_text=Column(Text,nullable=True)
    context_prompt=Column(Text,nullable=True)
    answer_text = Column(Text,nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

