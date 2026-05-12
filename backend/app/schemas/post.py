from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import LinkedinTargetType, PostSource, PostStatus


class PostCreateRequest(BaseModel):
    body: str = Field(min_length=1)
    title_internal: str | None = Field(default=None, max_length=255)
    source: PostSource = PostSource.CUSTOM
    niche_slug: str | None = Field(default=None, max_length=120)
    hashtags: list[str] = Field(default_factory=list)
    first_comment: str | None = None
    timezone: str = Field(default="UTC", max_length=64)


class PostUpdateRequest(BaseModel):
    body: str = Field(min_length=1)
    title_internal: str | None = Field(default=None, max_length=255)
    hashtags: list[str] = Field(default_factory=list)
    first_comment: str | None = None
    change_reason: str | None = Field(default="manual_edit", max_length=255)


class PostRejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class PostScheduleRequest(BaseModel):
    scheduled_for: datetime
    timezone: str = Field(default="UTC", max_length=64)
    linkedin_target_type: LinkedinTargetType | None = None
    linkedin_target_urn: str | None = Field(default=None, max_length=255)


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    author_user_id: UUID
    status: PostStatus
    source: PostSource
    niche_slug: str | None = None
    title_internal: str | None = None
    body: str
    hashtags: list[str]
    first_comment: str | None = None
    scheduled_for: datetime | None = None
    timezone: str
    linkedin_target_type: LinkedinTargetType | None = None
    linkedin_target_urn: str | None = None
    linkedin_post_urn: str | None = None
    rejection_reason: str | None = None
    failure_reason: str | None = None


class PostListResponse(BaseModel):
    posts: list[PostResponse]


class PostVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    version_number: int
    body: str
    hashtags: list[str]
    first_comment: str | None = None
    change_reason: str | None = None


class PostVersionListResponse(BaseModel):
    versions: list[PostVersionResponse]
