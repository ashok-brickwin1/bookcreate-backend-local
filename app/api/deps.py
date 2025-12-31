# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID
from app.models.user import User

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.core.config import settings
from app.schemas.user import TokenPayload
from app.crud.user import get_user, get_user_by_email
from typing import Generator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=True)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print("Token received:", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(sub=payload.get("sub"))
        if token_data.sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, user_id=PyUUID(token_data.sub))
    print("Fetched user in get_current_user:", user)
    if not user:
        raise credentials_exception
    return user


def super_user_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    return current_user


def org_user_required(current_user: User = Depends(get_current_user)):
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization privileges required"
        )
    return current_user


def login_required(current_user: User = Depends(get_current_user)):
    if current_user.is_superuser:
        return current_user
    

    if not current_user.is_superuser:
        return current_user
    

    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )