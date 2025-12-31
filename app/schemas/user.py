# app/schemas/user.py
from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import BaseModel, Field

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=8)


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: UUID
    is_active: bool

    class Config:
        orm_mode = True

# token schema
class Token(BaseModel):
    access_token: str
    token_type: str
    user_email:str

class TokenPayload(BaseModel):
    sub: Optional[str] = None



class SuperUserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None



