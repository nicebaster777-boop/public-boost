"""Upload schemas."""

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """Image upload response schema."""

    url: str
    storage_path: str
    size: int
    mime_type: str
