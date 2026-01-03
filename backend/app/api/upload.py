"""Upload endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])


def require_extended_tier(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require extended subscription tier."""
    if current_user.subscription_tier != "extended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires 'extended' subscription tier",
        )
    return current_user


ALLOWED_MIME_TYPES = ["image/jpeg", "image/jpg", "image/png"]
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@router.post("/image", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_extended_tier),
):
    """Upload an image for post."""
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024 * 1024)} MB",
        )

    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # Validate file extension
    file_extension = Path(file.filename).suffix.lower() if file.filename else ""
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Generate unique filename
    file_id = uuid.uuid4()
    filename = f"{file_id}{file_extension}"

    # Create upload directory if it doesn't exist
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_path / filename
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Generate URL (for MVP, use relative path; in production, use full URL with CDN)
    storage_path = f"{settings.upload_dir}/{filename}"
    # In production, this should be a full URL like: f"{settings.media_url}/{storage_path}"
    url = f"/{storage_path}"

    return {
        "data": {
            "url": url,
            "storage_path": storage_path,
            "size": file_size,
            "mime_type": file.content_type,
        }
    }
