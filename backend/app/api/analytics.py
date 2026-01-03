"""Analytics endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.analytics import AnalyticsSnapshot
from app.models.community import Community
from app.models.user import User
from app.schemas.analytics import (
    AccountHealth,
    CommunityAnalyticsResponse,
    CommunityMetricDetail,
    CommunityMetrics,
    DashboardResponse,
    MetricValue,
    Recommendation,
    RecommendationsResponse,
    SubscriberDynamics,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    date_from: datetime | None = Query(None, description="Start date for metrics (ISO 8601)"),
    date_to: datetime | None = Query(None, description="End date for metrics (ISO 8601)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard analytics for all user's communities."""
    # Set default date range (30 days ago to now)
    now = datetime.now(timezone.utc)
    if date_to is None:
        date_to = now
    if date_from is None:
        date_from = date_to - timedelta(days=30)

    # Get all active communities for user
    communities_result = await db.execute(
        select(Community).where(
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
            Community.is_active == True,
        )
    )
    communities = communities_result.scalars().all()

    # Get latest metrics for each community
    community_metrics_list = []
    total_reach = 0.0
    total_new_subscribers = 0.0
    total_engagement = 0.0
    active_communities_count = 0

    for community in communities:
        # Get latest follower_count snapshot
        latest_followers_result = await db.execute(
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.community_id == community.id,
                AnalyticsSnapshot.metric_name == "follower_count",
            )
            .order_by(AnalyticsSnapshot.recorded_at.desc())
            .limit(1)
        )
        latest_followers = latest_followers_result.scalar_one_or_none()

        # Get previous follower_count for growth calculation
        previous_followers_result = await db.execute(
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.community_id == community.id,
                AnalyticsSnapshot.metric_name == "follower_count",
                AnalyticsSnapshot.recorded_at < date_from,
            )
            .order_by(AnalyticsSnapshot.recorded_at.desc())
            .limit(1)
        )
        previous_followers = previous_followers_result.scalar_one_or_none()

        # Get latest engagement_rate
        latest_engagement_result = await db.execute(
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.community_id == community.id,
                AnalyticsSnapshot.metric_name == "engagement_rate",
            )
            .order_by(AnalyticsSnapshot.recorded_at.desc())
            .limit(1)
        )
        latest_engagement = latest_engagement_result.scalar_one_or_none()

        current_followers = int(latest_followers.metric_value) if latest_followers else 0
        previous_followers_value = int(previous_followers.metric_value) if previous_followers else 0
        follower_growth = current_followers - previous_followers_value
        engagement_rate = float(latest_engagement.metric_value) if latest_engagement else 0.0

        if latest_followers:
            active_communities_count += 1
            total_reach += current_followers
            total_new_subscribers += follower_growth
            total_engagement += engagement_rate

        community_metrics_list.append(
            CommunityMetrics(
                id=community.id,
                name=community.name,
                platform=community.platform,
                current_followers=current_followers,
                follower_growth=follower_growth,
                engagement_rate=engagement_rate,
                last_sync_at=community.last_sync_at,
            )
        )

    # Calculate account health score (0-10)
    # Factors: token validity, sync status, engagement trends
    health_score = 0
    max_score = 10

    # Check token validity (2 points)
    valid_tokens = sum(
        1
        for c in communities
        if (c.platform == "telegram" and c.bot_token_encrypted)
        or (
            c.platform == "vk"
            and c.access_token_encrypted
            and (c.token_expires_at is None or c.token_expires_at.replace(tzinfo=timezone.utc) > now)
        )
    )
    if communities:
        health_score += min(2, (valid_tokens / len(communities)) * 2)

    # Check sync status (3 points)
    synced_communities = sum(
        1
        for c in communities
        if c.last_sync_at
        and (now - c.last_sync_at.replace(tzinfo=timezone.utc)).days < 7
    )
    if communities:
        health_score += min(3, (synced_communities / len(communities)) * 3)

    # Engagement rate (5 points) - normalized to 0-10
    avg_engagement = total_engagement / active_communities_count if active_communities_count > 0 else 0
    # Assume 10% engagement is perfect (5 points)
    health_score += min(5, (avg_engagement / 10.0) * 5)

    account_health = AccountHealth(
        score=int(health_score),
        max_score=max_score,
        metrics={
            "total_reach": total_reach,
            "new_subscribers": total_new_subscribers,
            "engagement_rate": round(total_engagement / active_communities_count, 2) if active_communities_count > 0 else 0.0,
        },
    )

    # Build subscriber dynamics
    # Get follower counts per platform over time period
    dynamics_data = []
    for platform in ["vk", "telegram"]:
        platform_communities = [c for c in communities if c.platform == platform]
        if not platform_communities:
            continue

        # Get snapshots grouped by date
        platform_ids = [c.id for c in platform_communities]
        snapshots_result = await db.execute(
            select(
                func.date(AnalyticsSnapshot.recorded_at).label("date"),
                func.sum(AnalyticsSnapshot.metric_value).label("total_followers"),
            )
            .where(
                AnalyticsSnapshot.community_id.in_(platform_ids),
                AnalyticsSnapshot.metric_name == "follower_count",
                AnalyticsSnapshot.recorded_at >= date_from,
                AnalyticsSnapshot.recorded_at <= date_to,
            )
            .group_by(func.date(AnalyticsSnapshot.recorded_at))
            .order_by(func.date(AnalyticsSnapshot.recorded_at))
        )
        snapshots = snapshots_result.all()

        for snapshot in snapshots:
            dynamics_data.append({
                "date": snapshot.date.isoformat(),
                "platform": platform,
                "followers": int(snapshot.total_followers),
            })

    subscriber_dynamics = SubscriberDynamics(
        period=f"{date_from.isoformat()} to {date_to.isoformat()}",
        data=dynamics_data,
    )

    return DashboardResponse(
        account_health=account_health,
        communities=community_metrics_list,
        subscriber_dynamics=subscriber_dynamics,
    )


@router.get("/communities/{community_id}", response_model=CommunityAnalyticsResponse)
async def get_community_analytics(
    community_id: UUID,
    date_from: datetime | None = Query(None, description="Start date (ISO 8601)"),
    date_to: datetime | None = Query(None, description="End date (ISO 8601)"),
    metric: str | None = Query(None, description="Filter by metric name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed analytics for a specific community."""
    # Verify community belongs to user
    community_result = await db.execute(
        select(Community).where(
            Community.id == community_id,
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
        )
    )
    community = community_result.scalar_one_or_none()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    # Set default date range
    now = datetime.now(timezone.utc)
    if date_to is None:
        date_to = now
    if date_from is None:
        date_from = date_to - timedelta(days=30)

    # Build query for snapshots
    query = select(AnalyticsSnapshot).where(
        AnalyticsSnapshot.community_id == community_id,
        AnalyticsSnapshot.recorded_at >= date_from,
        AnalyticsSnapshot.recorded_at <= date_to,
    )

    if metric:
        query = query.where(AnalyticsSnapshot.metric_name == metric)

    result = await db.execute(query.order_by(AnalyticsSnapshot.metric_name, AnalyticsSnapshot.recorded_at))
    snapshots = result.scalars().all()

    # Group snapshots by metric_name
    metrics_dict: dict[str, list[AnalyticsSnapshot]] = {}
    for snapshot in snapshots:
        if snapshot.metric_name not in metrics_dict:
            metrics_dict[snapshot.metric_name] = []
        metrics_dict[snapshot.metric_name].append(snapshot)

    # Build metric details with trends
    metric_details = []
    for metric_name, metric_snapshots in metrics_dict.items():
        # Sort by recorded_at
        metric_snapshots.sort(key=lambda x: x.recorded_at)

        values = [
            MetricValue(value=float(snapshot.metric_value), recorded_at=snapshot.recorded_at)
            for snapshot in metric_snapshots
        ]

        # Calculate trend and change_percent
        if len(values) >= 2:
            first_value = values[0].value
            last_value = values[-1].value
            change_percent = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0.0

            if change_percent > 1.0:
                trend = "up"
            elif change_percent < -1.0:
                trend = "down"
            else:
                trend = "stable"
        else:
            change_percent = 0.0
            trend = "stable"

        metric_details.append(
            CommunityMetricDetail(
                metric_name=metric_name,
                values=values,
                trend=trend,
                change_percent=round(change_percent, 2),
            )
        )

    return CommunityAnalyticsResponse(
        community={
            "id": community.id,
            "name": community.name,
            "platform": community.platform,
        },
        metrics=metric_details,
        period={
            "from": date_from,
            "to": date_to,
        },
    )


@router.post("/communities/{community_id}/refresh")
async def refresh_community_analytics(
    community_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger analytics refresh for a community."""
    # Verify community belongs to user
    community_result = await db.execute(
        select(Community).where(
            Community.id == community_id,
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
        )
    )
    community = community_result.scalar_one_or_none()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    # TODO: Enqueue background task to fetch analytics from external API
    # For MVP, just update last_sync_at timestamp
    # In production, this should enqueue a Celery task
    community.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()

    return {
        "message": "Analytics refresh initiated",
        "data": {
            "community_id": community_id,
            "status": "pending",
        },
    }


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated recommendations (if available)."""
    # Check if we have enough data (at least 7 days of snapshots)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    communities_result = await db.execute(
        select(Community).where(
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
            Community.is_active == True,
        )
    )
    communities = communities_result.scalars().all()

    if not communities:
        return RecommendationsResponse(recommendations=[])

    # Check if we have snapshots in the last 7 days
    has_recent_data = False
    for community in communities:
        snapshot_result = await db.execute(
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.community_id == community.id,
                AnalyticsSnapshot.recorded_at >= seven_days_ago,
            )
            .limit(1)
        )
        if snapshot_result.scalar_one_or_none():
            has_recent_data = True
            break

    if not has_recent_data:
        return RecommendationsResponse(recommendations=[])

    # TODO: Generate actual recommendations based on analytics data
    # For MVP, return empty array or placeholder recommendations
    # In production, this should use ML/AI to analyze patterns

    recommendations = []
    # Example placeholder recommendation
    # recommendations.append(
    #     Recommendation(
    #         id=uuid4(),
    #         type="schedule_post",
    #         priority="medium",
    #         title="Запланируйте пост в среду",
    #         description="Посты в среду показывают лучшую вовлеченность",
    #         action={"type": "create_post", "suggested_time": "2024-01-17T14:00:00Z", "platform": "vk"},
    #     )
    # )

    return RecommendationsResponse(recommendations=recommendations)
