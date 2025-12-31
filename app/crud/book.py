from sqlalchemy.orm import Session
from uuid import UUID
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def create_book(db: Session, data: BookCreate) -> Book:
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: UUID) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def get_books_for_book_user(db: Session, book_user_id: UUID):
    return db.query(Book).filter(
        Book.book_user_id == book_user_id,
        Book.is_deleted == False
    ).all()


def update_book(db: Session, book: Book, data: BookUpdate) -> Book:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book
