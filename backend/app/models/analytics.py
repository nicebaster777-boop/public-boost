"""Analytics model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalyticsSnapshot(Base):
    """Analytics snapshot model."""

    __tablename__ = "analytics_snapshots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(
        ForeignKey("communities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, index=True)
    metric_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    community: Mapped["Community"] = relationship("Community", back_populates="analytics_snapshots")

    # Indexes
    __table_args__ = (
        Index("idx_analytics_snapshots_metric", "community_id", "metric_name", "recorded_at"),
        Index("idx_analytics_snapshots_latest", "community_id", "recorded_at"),
    )

