"""User endpoints."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    if user_update.timezone is not None:
        current_user.timezone = user_update.timezone
    if user_update.subscription_tier is not None:
        if user_update.subscription_tier not in ["basic", "extended"]:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="subscription_tier must be 'basic' or 'extended'"
            )
        current_user.subscription_tier = user_update.subscription_tier
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)
