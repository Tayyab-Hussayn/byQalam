from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PostMediaCreateRequest(BaseModel):
    storage_path: str = Field(min_length=1, max_length=1024)
    media_type: str = Field(min_length=1, max_length=80)
    original_filename: str | None = Field(default=None, max_length=255)
    size_bytes: int | None = Field(default=None, ge=0)


class PostMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    storage_path: str
    media_type: str
    original_filename: str | None = None
    size_bytes: int | None = None
