"""Calendar endpoints."""

from calendar import monthrange
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.community import Community
from app.models.post import Post, PostPublication
from app.models.user import User
from app.schemas.calendar import CalendarCommunity, CalendarPost, CalendarResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])


def require_extended_tier(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require extended subscription tier."""
    if current_user.subscription_tier != "extended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires 'extended' subscription tier",
        )
    return current_user


@router.get("", response_model=CalendarResponse)
async def get_calendar(
    month: int | None = Query(None, ge=1, le=12, description="Month number (1-12)"),
    year: int | None = Query(None, ge=2000, description="Year"),
    community_id: UUID | None = Query(None, description="Filter by community"),
    current_user: User = Depends(require_extended_tier),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar view of scheduled posts."""
    # Set default to current month/year
    now = datetime.now(timezone.utc)
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    # Calculate date range for the month
    _, last_day = monthrange(year, month)
    month_start = datetime(year, month, 1, tzinfo=timezone.utc)
    month_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    # Build query for posts scheduled in this month
    query = select(Post).where(
        Post.user_id == current_user.id,
        Post.scheduled_at.isnot(None),
        Post.scheduled_at >= month_start,
        Post.scheduled_at <= month_end,
    )

    # Filter by community if provided
    if community_id:
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

        # Filter posts by community through publications
        query = query.join(PostPublication).where(PostPublication.community_id == community_id)

    # Execute query
    result = await db.execute(query.order_by(Post.scheduled_at))
    posts = result.scalars().all()

    # Build calendar posts with communities
    calendar_posts = []
    for post in posts:
        # Get communities for this post
        pub_result = await db.execute(
            select(PostPublication, Community)
            .join(Community, PostPublication.community_id == Community.id)
            .where(PostPublication.post_id == post.id)
        )
        publications_data = pub_result.all()

        communities = []
        for pub, community in publications_data:
            communities.append(
                CalendarCommunity(
                    id=community.id,
                    name=community.name,
                    platform=community.platform,
                )
            )

        calendar_posts.append(
            CalendarPost(
                id=post.id,
                content_text=post.content_text,
                scheduled_at=post.scheduled_at,
                status=post.status,
                communities=communities,
            )
        )

    return CalendarResponse(
        month=month,
        year=year,
        posts=calendar_posts,
    )
