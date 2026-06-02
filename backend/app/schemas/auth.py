import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# --- Requests ---

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)


# --- Responses ---

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user id
    type: str  # "access" or "refresh"
    exp: Optional[int] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True
