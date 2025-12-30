"""Posts endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.community import Community
from app.models.post import Post, PostPublication
from app.models.user import User
from app.schemas.post import PostCreate, PostListResponse, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


def require_extended_tier(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require extended subscription tier."""
    if current_user.subscription_tier != "extended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires 'extended' subscription tier",
        )
    return current_user


def validate_scheduled_at(scheduled_at: datetime | None) -> None:
    """Validate scheduled_at is in future and not more than 30 days ahead."""
    if scheduled_at is None:
        return

    now = datetime.now(timezone.utc)
    max_future = now + timedelta(days=30)

    if scheduled_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scheduled_at must be in the future",
        )

    if scheduled_at > max_future:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scheduled_at cannot be more than 30 days in the future",
        )


@router.get("", response_model=PostListResponse)
async def get_posts(
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    community_id: UUID | None = Query(None, description="Filter by target community"),
    scheduled_from: datetime | None = Query(None, description="Filter posts scheduled from date"),
    scheduled_to: datetime | None = Query(None, description="Filter posts scheduled to date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_extended_tier),
    db: AsyncSession = Depends(get_db),
):
    """Get list of user's posts."""
    # Build query
    query = select(Post).where(Post.user_id == current_user.id)

    # Apply filters
    if status_filter:
        valid_statuses = ["draft", "scheduled", "publishing", "published", "failed", "partially_published"]
        if status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {', '.join(valid_statuses)}",
            )
        query = query.where(Post.status == status_filter)

    if community_id:
        # Filter by community through publications
        query = query.join(PostPublication).where(PostPublication.community_id == community_id)

    if scheduled_from:
        query = query.where(Post.scheduled_at >= scheduled_from)

    if scheduled_to:
        query = query.where(Post.scheduled_at <= scheduled_to)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Post.created_at.desc()).offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    posts = result.scalars().all()

    # Load publications for each post
    for post in posts:
        await db.execute(
            select(PostPublication)
            .where(PostPublication.post_id == post.id)
            .options()
        )

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    # Build response with publications
    post_responses = []
    for post in posts:
        # Get publications for this post
        pub_result = await db.execute(
            select(PostPublication, Community)
            .join(Community, PostPublication.community_id == Community.id)
            .where(PostPublication.post_id == post.id)
        )
        publications_data = pub_result.all()

        publications = []
        for pub, community in publications_data:
            publications.append({
                "id": pub.id,
                "community_id": pub.community_id,
                "community_name": community.name,
                "platform": community.platform,
                "status": pub.status,
                "external_post_id": pub.external_post_id,
                "published_at": pub.published_at,
                "error_message": pub.error_message,
            })

        post_dict = {
            "id": post.id,
            "content_text": post.content_text,
            "image_url": post.image_url,
            "scheduled_at": post.scheduled_at,
            "status": post.status,
            "error_message": post.error_message,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "publications": publications,
        }
        post_responses.append(PostResponse.model_validate(post_dict))

    return PostListResponse(
        data=post_responses,
        pagination={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    current_user: User = Depends(require_extended_tier),
    db: AsyncSession = Depends(get_db),
):
    """Get post details."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Get publications
    pub_result = await db.execute(
        select(PostPublication, Community)
        .join(Community, PostPublication.community_id == Community.id)
        .where(PostPublication.post_id == post.id)
    )
    publications_data = pub_result.all()

    publications = []
    for pub, community in publications_data:
        publications.append({
            "id": pub.id,
            "community_id": pub.community_id,
            "community_name": community.name,
            "platform": community.platform,
            "status": pub.status,
            "external_post_id": pub.external_post_id,
            "published_at": pub.published_at,
            "error_message": pub.error_message,
        })

    post_dict = {
        "id": post.id,
        "content_text": post.content_text,
        "image_url": post.image_url,
        "scheduled_at": post.scheduled_at,
        "status": post.status,
        "error_message": post.error_message,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "publications": publications,
    }

    return PostResponse.model_validate(post_dict)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: PostCreate,
    current_user: User = Depends(require_extended_tier),
    db: AsyncSession = Depends(get_db),
):
    """Create a new post."""
    # Validate scheduled_at
    validate_scheduled_at(request.scheduled_at)

    # Determine status
    post_status = "scheduled" if request.scheduled_at else "draft"

    # Validate community_ids if scheduled
    if request.scheduled_at:
        if not request.community_ids or len(request.community_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="community_ids is required when scheduled_at is provided",
            )

    # Validate communities exist and belong to user
    if request.community_ids:
        communities_result = await db.execute(
            select(Community).where(
                Community.id.in_(request.community_ids),
                Community.user_id == current_user.id,
                Community.deleted_at.is_(None),
                Community.is_active == True,
            )
        )
        communities = communities_result.scalars().all()

        if len(communities) != len(request.community_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more communities not found or not active",
            )

    # Create post
    post = Post(
        user_id=current_user.id,
        content_text=request.content_text,
        image_url=request.image_url,
        scheduled_at=request.scheduled_at,
        status=post_status,
    )

    db.add(post)
    await db.flush()  # Get post.id

    # Create publications if scheduled
    if request.scheduled_at and request.community_ids:
        for community_id in request.community_ids:
            publication = PostPublication(
                post_id=post.id,
                community_id=community_id,
                status="pending",
            )
            db.add(publication)

    await db.commit()
    await db.refresh(post)

    # TODO: Enqueue task in Celery if scheduled
    # For MVP, we'll skip this

    # Get publications for response
    publications = []
    if request.community_ids:
        pub_result = await db.execute(
            select(PostPublication, Community)
            .join(Community, PostPublication.community_id == Community.id)
            .where(PostPublication.post_id == post.id)
        )
        publications_data = pub_result.all()

        for pub, community in publications_data:
            publications.append({
                "id": pub.id,
                "community_id": pub.community_id,
                "community_name": community.name,
                "platform": community.platform,
                "status": pub.status,
                "external_post_id": pub.external_post_id,
                "published_at": pub.published_at,
                "error_message": pub.error_message,
            })

    post_dict = {
        "id": post.id,
        "content_text": post.content_text,
        "image_url": post.image_url,
        "scheduled_at": post.scheduled_at,
        "status": post.status,
        "error_message": post.error_message,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "publications": publications,
    }

    return PostResponse.model_validate(post_dict)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    request: PostUpdate,
    current_user: User = Depends(require_extended_tier),
    db: AsyncSession = Depends(get_db),
):
    """Update a post (only if status is draft or scheduled)."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check status
    if post.status not in ["draft", "scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post can only be updated when status is 'draft' or 'scheduled'",
        )

    # Validate scheduled_at if provided
    new_scheduled_at = request.scheduled_at if request.scheduled_at is not None else post.scheduled_at
    validate_scheduled_at(new_scheduled_at)

    # Update fields
    if request.content_text is not None:
        post.content_text = request.content_text
    if request.image_url is not None:
        post.image_url = request.image_url
    if request.scheduled_at is not None:
        post.scheduled_at = request.scheduled_at
        # Update status if scheduled_at changed
        if request.scheduled_at and post.status == "draft":
            post.status = "scheduled"
        elif request.scheduled_at is None and post.status == "scheduled":
            post.status = "draft"

    # Update publications if community_ids provided
    if request.community_ids is not None:
        # Validate communities
        communities_result = await db.execute(
            select(Community).where(
                Community.id.in_(request.community_ids),
                Community.user_id == current_user.id,
                Community.deleted_at.is_(None),
                Community.is_active == True,
            )
        )
        communities = communities_result.scalars().all()

        if len(communities) != len(request.community_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more communities not found or not active",
            )

        # Delete existing publications
        existing_pubs_result = await db.execute(
            select(PostPublication).where(PostPublication.post_id == post.id)
        )
        existing_pubs = existing_pubs_result.scalars().all()
        for pub in existing_pubs:
            await db.delete(pub)

        # Create new publications
        for community_id in request.community_ids:
            publication = PostPublication(
                post_id=post.id,
                community_id=community_id,
                status="pending",
            )
            db.add(publication)

    await db.commit()
    await db.refresh(post)

    # Get publications for response
    pub_result = await db.execute(
        select(PostPublication, Community)
        .join(Community, PostPublication.community_id == Community.id)
        .where(PostPublication.post_id == post.id)
    )
    publications_data = pub_result.all()

    publications = []
    for pub, community in publications_data:
        publications.append({
            "id": pub.id,
            "community_id": pub.community_id,
            "community_name": community.name,
            "platform": community.platform,
            "status": pub.status,
            "external_post_id": pub.external_post_id,
            "published_at": pub.published_at,
            "error_message": pub.error_message,
        })

    post_dict = {
        "id": post.id,
        "content_text": post.content_text,
        "image_url": post.image_url,
        "scheduled_at": post.scheduled_at,
        "status": post.status,
        "error_message": post.error_message,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "publications": publications,
    }

    return PostResponse.model_validate(post_dict)


@router.delete("/{post_id}")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(require_extended_tier),
    db: AsyncSession = Depends(get_db),
):
    """Delete a post (only if status is draft or scheduled)."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check status
    if post.status not in ["draft", "scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post can only be deleted when status is 'draft' or 'scheduled'",
        )

    # TODO: Cancel scheduled task if exists

    await db.delete(post)
    await db.commit()

    return {"message": "Post deleted successfully"}
