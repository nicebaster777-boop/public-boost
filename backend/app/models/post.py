"""Post models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Post(Base):
    """Post model."""

    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="posts")
    publications: Mapped[list["PostPublication"]] = relationship(
        "PostPublication", back_populates="post", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_posts_user_status", "user_id", "status"),
        Index("idx_posts_scheduled_pending", "scheduled_at", "status", postgresql_where=(status == "scheduled")),
        Index("idx_posts_scheduled_at", "scheduled_at", postgresql_where=(scheduled_at.isnot(None))),
    )


class PostPublication(Base):
    """Post publication model."""

    __tablename__ = "post_publications"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    community_id: Mapped[UUID] = mapped_column(
        ForeignKey("communities.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    external_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    post: Mapped["Post"] = relationship("Post", back_populates="publications")
    community: Mapped["Community"] = relationship("Community", back_populates="post_publications")

    # Indexes
    __table_args__ = (
        Index("idx_post_publications_pending", "post_id", "status", postgresql_where=(status == "pending")),
        Index(
            "idx_post_publications_external_id",
            "community_id",
            "external_post_id",
            postgresql_where=(external_post_id.isnot(None)),
        ),
    )
