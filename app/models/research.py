import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.db.base import Base



class SourceSite(Base):
    """WHILE CREATING SOURCE SITES WE SEE 
    DIFFERENT OPTIONS FROM WHICH WE CAN SELET LIKE INSTAGRAM , FACEBOOK ETC """
    __tablename__ = "source_site"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title=Column(Text, nullable=False)
    description=Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    



class ResearchSource(Base):
    """WHEN USER GIVE DATA ABOUT THEIR SOURCES WE STORE SOURCE SITE AND URL HERE
    THIS ALSO STORES THE FOR A BOOK USER THE SCRAPPED DATA OF RESPECTIVE SITES
    (we will be giving default source site if missing)
    """
    __tablename__ = "research_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_user_id = Column(UUID(as_uuid=True), ForeignKey("book_users.id"), nullable=False)
    source_site_id =Column(UUID(as_uuid=True), ForeignKey("source_site.id"), nullable=True)
    source_site=Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    help_text = Column(Text,nullable=True)
    raw_scraped_text = Column(Text,nullable=True)
    cleaned_text = Column(Text,nullable=True)
    source_metadata = Column("metadata", JSON,nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
