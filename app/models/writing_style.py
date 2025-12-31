
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class StyleContentType(Base):

    """TO STORE THE DIFFERENT TYPES OF STYLES AVAILABLE OR TO GENEREATE NEW ONE 
    WHILE CREATING CUSTOM WRITING STYLE"""
    __tablename__ = "style_content_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



    


class Style(Base):

    """TO CREATE STYLE OF A BOOK THAT WILL BE ADDED IN THE BOOK TABLE USING FOREIGNKEY"""
    __tablename__ = "styles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    content_type_id = Column(UUID(as_uuid=True), ForeignKey("style_content_types.id"), nullable=True)
    url = Column(String(255))
    pasted_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

