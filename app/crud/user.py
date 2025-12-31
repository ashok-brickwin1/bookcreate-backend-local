# app/crud/crud_user.py
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID


from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: PyUUID):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate, is_superuser: bool = False):
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_superuser=is_superuser  # Set superuser flag here
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> None:
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()