# Central declarative Base + model registry
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
# Helpful naming convention (great for Alembic)
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
_metadata = MetaData(naming_convention=NAMING_CONVENTION)

class Base(DeclarativeBase):
    metadata = _metadata

from app.models.user import User
from app.models.book_user import BookUser
from app.models.book import Book, BookType
from app.models.chapter import Chapter
from app.models.life_moment import LifeMoment, LifeStage
from app.models.prompt import Prompt
from app.models.question import Question, QuestionType,Answer
from app.models.influence import InfluenceType, InfluencingQuestion, ContentType
from app.models.research import ResearchSource, SourceSite
from app.models.twin import Twin
from app.models.vision import VisionAnswers, VisionQuestion, VisionQuestionType
from app.models.writing_style import Style, StyleContentType


__all__ = [
"Base",
"User",
"BookUser",
"Book",
"BookType",
"Chapter",
"LifeMoment",
"LifeStage",
"Prompt",
"Question",
"QuestionType",
"InfluenceType",
"InfluencingQuestion",
"ContentType",
"Answer",
"ResearchSource",
"SourceSite",
"Twin",
"VisionAnswers",
"VisionQuestion",
"VisionQuestionType",
"Style",
"StyleContentType"
]