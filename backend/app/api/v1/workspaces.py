from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.models.enums import WorkspaceRole
from app.db.session import get_db_session
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceInviteAcceptRequest,
    WorkspaceInviteListResponse,
    WorkspaceInviteRequest,
    WorkspaceInviteResponse,
    WorkspaceListResponse,
    WorkspaceMemberListResponse,
    WorkspaceMemberResponse,
    WorkspaceMemberUpdateRequest,
    WorkspaceResponse,
)
from app.services.workspaces import (
    accept_workspace_invite,
    create_workspace,
    create_workspace_invite,
    list_user_workspaces,
    list_workspace_invites,
    list_workspace_members,
    remove_workspace_member,
    update_workspace_member_role,
)

router = APIRouter(prefix="/workspaces")


@router.get("", response_model=WorkspaceListResponse)
async def list_workspaces(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceListResponse:
    memberships = await list_user_workspaces(session, current_user.user)
    return WorkspaceListResponse(
        workspaces=[
            WorkspaceResponse.model_validate(workspace).model_copy(
                update={"role": role}
            )
            for workspace, role in memberships
        ]
    )


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace_endpoint(
    payload: WorkspaceCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceResponse:
    workspace = await create_workspace(
        session=session,
        user=current_user.user,
        name=payload.name,
        timezone=payload.timezone,
    )
    return WorkspaceResponse.model_validate(workspace).model_copy(
        update={"role": "owner"}
    )


@router.get("/{workspace_id}/members", response_model=WorkspaceMemberListResponse)
async def read_workspace_members(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceMemberListResponse:
    await _require_owner_or_admin(session, current_user, workspace_id)
    members = await list_workspace_members(session, workspace_id)
    return WorkspaceMemberListResponse(
        members=[WorkspaceMemberResponse.model_validate(member) for member in members]
    )


@router.post(
    "/{workspace_id}/invites",
    response_model=WorkspaceInviteResponse,
    status_code=201,
)
async def create_workspace_invite_endpoint(
    workspace_id: UUID,
    payload: WorkspaceInviteRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceInviteResponse:
    await _require_owner_or_admin(session, current_user, workspace_id)
    invite, token = await create_workspace_invite(
        session,
        workspace_id,
        current_user.user,
        payload.email,
        payload.role,
    )
    return WorkspaceInviteResponse(
        id=invite.id,
        workspace_id=invite.workspace_id,
        invited_by_user_id=invite.invited_by_user_id,
        email=invite.email,
        role=invite.role,
        expires_at=invite.expires_at,
        accepted_at=invite.accepted_at,
        revoked_at=invite.revoked_at,
        invite_token=token,
    )


@router.get("/{workspace_id}/invites", response_model=WorkspaceInviteListResponse)
async def read_workspace_invites(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceInviteListResponse:
    await _require_owner_or_admin(session, current_user, workspace_id)
    invites = await list_workspace_invites(session, workspace_id)
    return WorkspaceInviteListResponse(
        invites=[
            WorkspaceInviteResponse(
                id=invite.id,
                workspace_id=invite.workspace_id,
                invited_by_user_id=invite.invited_by_user_id,
                email=invite.email,
                role=invite.role,
                expires_at=invite.expires_at,
                accepted_at=invite.accepted_at,
                revoked_at=invite.revoked_at,
            )
            for invite in invites
        ]
    )


@router.post("/invites/accept", response_model=WorkspaceMemberResponse)
async def accept_workspace_invite_endpoint(
    payload: WorkspaceInviteAcceptRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceMemberResponse:
    member = await accept_workspace_invite(session, current_user.user, payload.token)
    return WorkspaceMemberResponse.model_validate(member)


@router.patch(
    "/{workspace_id}/members/{member_id}",
    response_model=WorkspaceMemberResponse,
)
async def update_workspace_member_endpoint(
    workspace_id: UUID,
    member_id: UUID,
    payload: WorkspaceMemberUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceMemberResponse:
    await _require_owner_only(session, current_user, workspace_id)
    member = await update_workspace_member_role(
        session,
        workspace_id,
        member_id,
        payload.role,
    )
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "workspace_member_not_found",
                "message": "Workspace member was not found.",
            },
        )
    return WorkspaceMemberResponse.model_validate(member)


@router.delete(
    "/{workspace_id}/members/{member_id}",
    response_model=WorkspaceMemberResponse,
)
async def remove_workspace_member_endpoint(
    workspace_id: UUID,
    member_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceMemberResponse:
    await _require_owner_only(session, current_user, workspace_id)
    member = await remove_workspace_member(session, workspace_id, member_id)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "workspace_member_not_found",
                "message": "Workspace member was not found.",
            },
        )
    return WorkspaceMemberResponse.model_validate(member)


async def _require_owner_or_admin(
    session: AsyncSession,
    current_user: CurrentUser,
    workspace_id: UUID,
) -> None:
    await _require_workspace_role(
        session,
        current_user,
        workspace_id,
        {WorkspaceRole.OWNER, WorkspaceRole.ADMIN},
    )


async def _require_owner_only(
    session: AsyncSession,
    current_user: CurrentUser,
    workspace_id: UUID,
) -> None:
    await _require_workspace_role(
        session,
        current_user,
        workspace_id,
        {WorkspaceRole.OWNER},
    )


async def _require_workspace_role(
    session: AsyncSession,
    current_user: CurrentUser,
    workspace_id: UUID,
    roles: set[WorkspaceRole],
) -> None:
    from app.services.workspaces import require_workspace_role

    try:
        await require_workspace_role(session, current_user.user, workspace_id, roles)
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "workspace_forbidden",
                "message": "Workspace access is required.",
            },
        ) from exc
