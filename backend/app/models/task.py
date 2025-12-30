"""Scheduled task model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScheduledTask(Base):
    """Scheduled task model."""

    __tablename__ = "scheduled_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'publish_post', 'fetch_analytics', 'refresh_token'
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=True, index=True)
    community_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_scheduled_tasks_pending", "scheduled_at", "status", postgresql_where=(status == "pending")),
        Index("idx_scheduled_tasks_post_id", "post_id", postgresql_where=(post_id.isnot(None))),
        Index("idx_scheduled_tasks_community_id", "community_id", postgresql_where=(community_id.isnot(None))),
    )
