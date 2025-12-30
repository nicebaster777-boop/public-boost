"""Communities endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.security import encrypt_token
from app.models.community import Community
from app.models.user import User
from app.schemas.community import (
    CommunityCreate,
    CommunityListResponse,
    CommunityResponse,
    CommunityUpdate,
)

router = APIRouter(prefix="/communities", tags=["communities"])


@router.get("", response_model=CommunityListResponse)
async def get_communities(
    platform: str | None = Query(None, description="Filter by platform (vk, telegram)"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of user's communities."""
    # Build query
    query = select(Community).where(
        Community.user_id == current_user.id,
        Community.deleted_at.is_(None),  # Only active (not soft-deleted)
    )

    # Apply filters
    if platform:
        if platform not in ["vk", "telegram"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform must be 'vk' or 'telegram'",
            )
        query = query.where(Community.platform == platform)

    if is_active is not None:
        query = query.where(Community.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Community.created_at.desc()).offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    communities = result.scalars().all()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return CommunityListResponse(
        data=[CommunityResponse.model_validate(c) for c in communities],
        pagination={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(
    community_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get community details."""
    result = await db.execute(
        select(Community).where(
            Community.id == community_id,
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
        )
    )
    community = result.scalar_one_or_none()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    return CommunityResponse.model_validate(community)


@router.post("", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(
    request: CommunityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect a new community."""
    # Validate platform
    if request.platform not in ["vk", "telegram"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform must be 'vk' or 'telegram'",
        )

    # Validate token requirements based on platform
    if request.platform == "vk":
        if not request.access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="access_token is required for VK",
            )
        if request.bot_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bot_token must not be provided for VK",
            )
    elif request.platform == "telegram":
        if not request.bot_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bot_token is required for Telegram",
            )
        if request.access_token or request.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="access_token and refresh_token must not be provided for Telegram",
            )

    # Check if community already exists (not soft-deleted)
    existing = await db.execute(
        select(Community).where(
            Community.user_id == current_user.id,
            Community.platform == request.platform,
            Community.external_id == request.external_id,
            Community.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Community already connected",
        )

    # Create community
    community = Community(
        user_id=current_user.id,
        platform=request.platform,
        external_id=request.external_id,
        name=request.name,
    )

    # Encrypt and store tokens
    if request.platform == "vk":
        if request.access_token:
            community.access_token_encrypted = encrypt_token(request.access_token)
        if request.refresh_token:
            community.refresh_token_encrypted = encrypt_token(request.refresh_token)
        # TODO: Get token expiration from VK API
        # For now, set to 24 hours from now
        # Convert to UTC and remove timezone info for database storage
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        community.token_expires_at = expires_at.replace(tzinfo=None)
    elif request.platform == "telegram":
        if request.bot_token:
            community.bot_token_encrypted = encrypt_token(request.bot_token)
        # Telegram bot tokens don't expire
        community.token_expires_at = None

    db.add(community)
    await db.commit()
    await db.refresh(community)

    # TODO: Validate token and user permissions with external API
    # For MVP, we'll skip this validation for now

    return CommunityResponse.model_validate(community)


@router.patch("/{community_id}", response_model=CommunityResponse)
async def update_community(
    community_id: UUID,
    request: CommunityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update community details."""
    result = await db.execute(
        select(Community).where(
            Community.id == community_id,
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
        )
    )
    community = result.scalar_one_or_none()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    # Update fields
    if request.name is not None:
        community.name = request.name

    await db.commit()
    await db.refresh(community)

    return CommunityResponse.model_validate(community)


@router.post("/{community_id}/disconnect")
async def disconnect_community(
    community_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect (soft delete) a community."""
    result = await db.execute(
        select(Community).where(
            Community.id == community_id,
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
        )
    )
    community = result.scalar_one_or_none()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    # Soft delete
    community.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    community.is_active = False

    await db.commit()

    return {"message": "Community disconnected successfully"}


@router.post("/{community_id}/refresh-token")
async def refresh_community_token(
    community_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger token refresh (VK only)."""
    result = await db.execute(
        select(Community).where(
            Community.id == community_id,
            Community.user_id == current_user.id,
            Community.deleted_at.is_(None),
        )
    )
    community = result.scalar_one_or_none()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    if community.platform != "vk":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token refresh is only available for VK communities",
        )

    # TODO: Enqueue background task to refresh token
    # For MVP, just return success message
    # In production, this should enqueue a Celery task

    return {"message": "Token refresh initiated"}
