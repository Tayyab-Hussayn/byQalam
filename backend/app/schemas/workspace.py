from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import WorkspaceRole


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    timezone: str = Field(default="UTC", min_length=1, max_length=64)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    timezone: str
    role: WorkspaceRole | None = None


class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceResponse]


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    is_active: bool


class WorkspaceInviteRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: WorkspaceRole = WorkspaceRole.VIEWER


class WorkspaceInviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    invited_by_user_id: UUID
    email: str
    role: WorkspaceRole
    expires_at: datetime
    accepted_at: datetime | None = None
    revoked_at: datetime | None = None
    invite_token: str | None = None


class WorkspaceInviteAcceptRequest(BaseModel):
    token: str = Field(min_length=10)


class WorkspaceMemberListResponse(BaseModel):
    members: list[WorkspaceMemberResponse]


class WorkspaceInviteListResponse(BaseModel):
    invites: list[WorkspaceInviteResponse]


class WorkspaceMemberUpdateRequest(BaseModel):
    role: WorkspaceRole
