# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_db, get_current_user
from app.schemas.user import ChangePasswordRequest, UserCreate, UserOut, Token,SuperUserCreate
from app.crud.user import get_user_by_email, create_user
from app.core.security import verify_password, create_access_token,create_refresh_token
from app.core.config import settings
from app.api.deps import get_db,super_user_required,org_user_required,login_required
from app.core.security import get_password_hash
import logging, secrets, string
from app.core.utils import send_email
from pydantic import BaseModel
from jose import jwt
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def generate_random_password(length: int = 12) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for email: {user_in.email}")
    existing = get_user_by_email(db, user_in.email)
    if existing:
        logger.warning(f"Signup failed - email already registered: {user_in.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, UserCreate(**user_in.model_dump()), is_superuser=True)

    
    logger.info(f"Signup successful for email: {user_in.email}")
    return user



@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    # OAuth2PasswordRequestForm gives: username, password, scope, grant_type, client_id
    user = get_user_by_email(db, form_data.username)
    logger.info(f"User fetched: {user}")
    logger.info(f"Form data password: {form_data.password}")
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    

    access_token = create_access_token(subject=str(user.id))

    refresh_token = create_refresh_token(subject=str(user.id))
    response = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",
                "user_email": user.email}
    print("Access token created:", response)
    return response

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh_access_token(data: RefreshTokenRequest):
    try:
        payload = jwt.decode(
            data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401)

        user_id = payload.get("sub")
        new_access_token = create_access_token(subject=user_id)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    except Exception as e:
        print(e,'ERROR GOT')
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid")

@router.get("/me", response_model=UserOut)
def read_users_me(current_user=Depends(get_current_user)):
    logger.info(f"Current user: {current_user}")
    return current_user



