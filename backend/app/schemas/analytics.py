"""Analytics schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccountHealth(BaseModel):
    """Account health metrics."""

    score: int
    max_score: int
    metrics: dict[str, float]


class CommunityMetrics(BaseModel):
    """Community metrics."""

    id: UUID
    name: str
    platform: str
    current_followers: int
    follower_growth: int
    engagement_rate: float
    last_sync_at: datetime | None


class SubscriberDynamics(BaseModel):
    """Subscriber dynamics data."""

    period: str
    data: list[dict[str, int | str]]


class DashboardResponse(BaseModel):
    """Dashboard response schema."""

    account_health: AccountHealth
    communities: list[CommunityMetrics]
    subscriber_dynamics: SubscriberDynamics


class Recommendation(BaseModel):
    """Recommendation schema."""

    id: UUID
    type: str
    priority: str
    title: str
    description: str
    action: dict


class MetricValue(BaseModel):
    """Metric value with timestamp."""

    value: float
    recorded_at: datetime


class CommunityMetricDetail(BaseModel):
    """Detailed metric for a community."""

    metric_name: str
    values: list[MetricValue]
    trend: str  # 'up', 'down', 'stable'
    change_percent: float


class CommunityAnalyticsResponse(BaseModel):
    """Community analytics response schema."""

    community: dict[str, str | UUID]  # id, name, platform
    metrics: list[CommunityMetricDetail]
    period: dict[str, datetime]  # from, to


class RecommendationsResponse(BaseModel):
    """Recommendations response schema."""

    recommendations: list[Recommendation]
