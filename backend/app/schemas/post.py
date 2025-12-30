"""Post schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.community import CommunityResponse


class PostBase(BaseModel):
    """Base post schema."""

    content_text: str = Field(max_length=10000, description="Post text content")
    image_url: str | None = Field(default=None, description="Image URL from upload")


class PostCreate(PostBase):
    """Post creation schema."""

    scheduled_at: datetime | None = Field(default=None, description="Scheduled publication time (UTC)")
    community_ids: list[UUID] | None = Field(default=None, min_length=1, description="Target community IDs")


class PostUpdate(PostBase):
    """Post update schema."""

    content_text: str | None = Field(default=None, max_length=10000)
    image_url: str | None = Field(default=None)
    scheduled_at: datetime | None = Field(default=None)
    community_ids: list[UUID] | None = Field(default=None, min_length=1)


class PostPublicationResponse(BaseModel):
    """Post publication response schema."""

    id: UUID
    community_id: UUID
    community_name: str
    platform: str
    status: str
    external_post_id: str | None
    published_at: datetime | None
    error_message: str | None

    model_config = {"from_attributes": True}


class PostResponse(PostBase):
    """Post response schema."""

    id: UUID
    scheduled_at: datetime | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    publications: list[PostPublicationResponse] = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """Post list response schema."""

    data: list[PostResponse]
    pagination: dict
