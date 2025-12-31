
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class LifeStage(Base):
    "DIFFERENT TYPE OF LIFE STAGES COULD BE FOUNDATION , "
    "GROWTH AND CHANGE, MASTERY AND IMPACT OPTIONS WE SHOW WHILE CRETING LIFEMOMENT "
    __tablename__ = "life_stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title=Column(Text,nullable=True)



class LifeMoment(Base):
    """WE CREATE LIFE MOMENTS AT REVIEW YOUR STORY PAGE"""
    __tablename__ = "life_moments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)


    moment_type = Column(
        Enum("high", "low", name="moment_type"),
        nullable=True
    )
   
    

    year = Column(Integer,nullable=True)

    life_stage = Column(Text,nullable=True)

    what_happened = Column(Text,nullable=True)
    story = Column(Text,nullable=True)
    lesson_learned = Column(Text,nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

