# app/api/book_users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.book_user import BookUser
from app.models.user import User
from app.schemas.book_user import BookUserRead

router = APIRouter()


@router.get("/list", response_model=list[BookUserRead])
def list_book_users(
    db: Session = Depends(get_db),
):
    """
    Returns all book profiles created by the logged-in user
    """
    return (
        db.query(BookUser)
        .order_by(BookUser.created_at.desc())
        .all()
    )
