"""Community model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Community(Base):
    """Community model."""

    __tablename__ = "communities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'vk' or 'telegram'
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    bot_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="communities")
    post_publications: Mapped[list["PostPublication"]] = relationship(
        "PostPublication", back_populates="community", cascade="all, delete-orphan"
    )
    analytics_snapshots: Mapped[list["AnalyticsSnapshot"]] = relationship(
        "AnalyticsSnapshot", back_populates="community", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_communities_active", "user_id", "is_active", "deleted_at"),
        Index("idx_communities_token_expires", "token_expires_at", postgresql_where=(token_expires_at.isnot(None))),
    )
