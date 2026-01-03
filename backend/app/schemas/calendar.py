"""Calendar schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CalendarCommunity(BaseModel):
    """Community info for calendar."""

    id: UUID
    name: str
    platform: str


class CalendarPost(BaseModel):
    """Post info for calendar."""

    id: UUID
    content_text: str
    scheduled_at: datetime
    status: str
    communities: list[CalendarCommunity]


class CalendarResponse(BaseModel):
    """Calendar response schema."""

    month: int
    year: int
    posts: list[CalendarPost]
