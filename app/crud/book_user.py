from sqlalchemy.orm import Session
from uuid import UUID
from app.models.book_user import BookUser
from app.schemas.book_user import BookUserCreate,BookUserRead
import logging

# root logger
logger = logging.getLogger()

def create_book_user(db: Session, data: BookUserCreate) -> BookUserRead:
    logger.info(f"creating book user with data:{data}")
    
    book_user = BookUser(
        user_id=data.user_id,
        name=data.name,
        email=data.email,
        title=data.title,
        bio=data.bio
    )
    db.add(book_user)
    db.commit()
    db.refresh(book_user)
    return book_user


def get_book_user(db: Session, book_user_id: UUID) -> BookUser | None:
    return db.query(BookUser).filter(
        BookUser.id == book_user_id,
        BookUser.is_deleted == False
    ).first()


def get_book_users_for_user(db: Session, user_id: UUID):
    return db.query(BookUser).filter(
        BookUser.user_id == user_id,
        BookUser.is_deleted == False
    ).all()


def soft_delete_book_user(db: Session, book_user_id: UUID):
    book_user = get_book_user(db, book_user_id)
    if book_user:
        book_user.is_deleted = True
        db.commit()


def get_latest_book_user(db: Session, user_id: UUID):#Ashok
    return (
        db.query(BookUser)
        .filter(
            BookUser.user_id == user_id,
            BookUser.is_deleted == False
        )
        .order_by(BookUser.created_at.desc())
        .first()
    )