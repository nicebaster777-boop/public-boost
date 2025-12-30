"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    timezone: str = Field(default="UTC", description="IANA timezone identifier")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """User update schema."""

    timezone: str | None = Field(default=None, description="IANA timezone identifier")
    subscription_tier: str | None = Field(default=None, description="Subscription tier (basic, extended)")


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    subscription_tier: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    """Registration request schema."""

    pass


class TokenResponse(BaseModel):
    """Token response schema."""

    token: str
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    email: EmailStr
