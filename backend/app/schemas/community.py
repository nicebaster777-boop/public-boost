"""Community schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CommunityBase(BaseModel):
    """Base community schema."""

    platform: str = Field(description="Platform: 'vk' or 'telegram'")
    external_id: str = Field(description="Platform-specific ID")
    name: str = Field(max_length=255, description="Community display name")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """Validate platform value."""
        if v not in ["vk", "telegram"]:
            raise ValueError("Platform must be 'vk' or 'telegram'")
        return v


class CommunityCreate(CommunityBase):
    """Community creation schema."""

    access_token: str | None = Field(default=None, description="VK access token")
    refresh_token: str | None = Field(default=None, description="VK refresh token")
    bot_token: str | None = Field(default=None, description="Telegram bot token")


class CommunityUpdate(BaseModel):
    """Community update schema."""

    name: str | None = Field(default=None, max_length=255)


class CommunityResponse(CommunityBase):
    """Community response schema."""

    id: UUID
    is_active: bool
    token_expires_at: datetime | None
    last_sync_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommunityListResponse(BaseModel):
    """Community list response schema."""

    data: list[CommunityResponse]
    pagination: dict
