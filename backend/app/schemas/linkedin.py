from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import LinkedinConnectionStatus, LinkedinTargetType


class LinkedinConnectRequest(BaseModel):
    redirect_after: str | None = Field(default=None, max_length=1024)


class LinkedinConnectResponse(BaseModel):
    authorization_url: str
    expires_at: datetime


class LinkedinConnectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    target_type: LinkedinTargetType
    target_urn: str
    display_name: str | None
    status: LinkedinConnectionStatus
    token_expires_at: datetime | None
    scopes: list[str]
    created_at: datetime
    updated_at: datetime


class LinkedinConnectionListResponse(BaseModel):
    connections: list[LinkedinConnectionResponse]


class LinkedinOAuthCallbackResponse(BaseModel):
    connection: LinkedinConnectionResponse
    redirect_after: str | None = None


class LinkedinPublishNowResponse(BaseModel):
    post_id: UUID
    publish_attempt_id: UUID
    linkedin_post_urn: str
