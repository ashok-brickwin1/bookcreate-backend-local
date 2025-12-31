from sqlalchemy.orm import Session
from uuid import UUID
from app.models.chapter import Chapter
from app.schemas.chapter import ChapterCreate, ChapterUpdate


def create_chapter(db: Session, data: ChapterCreate) -> Chapter:
    chapter = Chapter(**data.model_dump())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def get_chapters_for_book(db: Session, book_id: UUID):
    return db.query(Chapter).filter(
        Chapter.book_id == book_id
    ).order_by(Chapter.chapter_index).all()


def update_chapter(db: Session, chapter: Chapter, data: ChapterUpdate) -> Chapter:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(chapter, field, value)
    db.commit()
    db.refresh(chapter)
    return chapter
