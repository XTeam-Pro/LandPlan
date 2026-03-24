"""User request/response schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""

    password: str
    role: str = "user"


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""

    id: int
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str
