from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.models.enums import WorkspaceRole
from app.db.session import get_db_session
from app.schemas.linkedin import (
    LinkedinConnectionListResponse,
    LinkedinConnectionResponse,
    LinkedinConnectRequest,
    LinkedinConnectResponse,
    LinkedinOAuthCallbackResponse,
    LinkedinPublishNowResponse,
)
from app.services.linkedin import (
    LinkedinConfigError,
    LinkedinOAuthError,
    complete_oauth_callback,
    create_connect_url,
    disconnect_connection,
    list_connections,
    publish_text_post,
)
from app.services.posts import get_post
from app.services.workspaces import require_workspace_role

router = APIRouter(prefix="/linkedin")

EDIT_ROLES = {WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.EDITOR}


@router.post(
    "/workspaces/{workspace_id}/connect",
    response_model=LinkedinConnectResponse,
)
async def create_linkedin_connect_url(
    workspace_id: UUID,
    payload: LinkedinConnectRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LinkedinConnectResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    try:
        authorization_url, state, _raw_state = await create_connect_url(
            session,
            workspace_id,
            current_user.user,
            payload.redirect_after,
        )
    except LinkedinConfigError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "linkedin_not_configured", "message": str(exc)},
        ) from exc
    return LinkedinConnectResponse(
        authorization_url=authorization_url,
        expires_at=state.expires_at,
    )


@router.get("/oauth/callback", response_model=LinkedinOAuthCallbackResponse)
async def linkedin_oauth_callback(
    state: Annotated[str, Query(min_length=20)],
    code: Annotated[str, Query(min_length=1)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LinkedinOAuthCallbackResponse:
    try:
        connection, oauth_state = await complete_oauth_callback(session, state, code)
    except LinkedinConfigError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "linkedin_not_configured", "message": str(exc)},
        ) from exc
    except LinkedinOAuthError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "linkedin_oauth_failed", "message": str(exc)},
        ) from exc
    return LinkedinOAuthCallbackResponse(
        connection=LinkedinConnectionResponse.model_validate(connection),
        redirect_after=oauth_state.redirect_after,
    )


@router.get(
    "/workspaces/{workspace_id}/connections",
    response_model=LinkedinConnectionListResponse,
)
async def read_linkedin_connections(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LinkedinConnectionListResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    connections = await list_connections(session, workspace_id)
    return LinkedinConnectionListResponse(
        connections=[
            LinkedinConnectionResponse.model_validate(connection)
            for connection in connections
        ]
    )


@router.delete(
    "/workspaces/{workspace_id}/connections/{connection_id}",
    response_model=LinkedinConnectionResponse,
)
async def delete_linkedin_connection(
    workspace_id: UUID,
    connection_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LinkedinConnectionResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    connection = await disconnect_connection(session, workspace_id, connection_id)
    if connection is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "linkedin_connection_not_found",
                "message": "LinkedIn connection was not found.",
            },
        )
    return LinkedinConnectionResponse.model_validate(connection)


@router.post(
    "/workspaces/{workspace_id}/posts/{post_id}/publish-now",
    response_model=LinkedinPublishNowResponse,
)
async def publish_linkedin_post_now(
    workspace_id: UUID,
    post_id: UUID,
    connection_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LinkedinPublishNowResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await get_post(session, workspace_id, post_id)
    if post is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "post_not_found", "message": "Post was not found."},
        )
    connections = await list_connections(session, workspace_id)
    connection = next(
        (candidate for candidate in connections if candidate.id == connection_id),
        None,
    )
    if connection is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "linkedin_connection_not_found",
                "message": "LinkedIn connection was not found.",
            },
        )
    attempt = await publish_text_post(session, post, connection)
    if attempt.linkedin_post_urn is None:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "linkedin_publish_failed",
                "message": attempt.error_message or "LinkedIn publishing failed.",
            },
        )
    return LinkedinPublishNowResponse(
        post_id=post.id,
        publish_attempt_id=attempt.id,
        linkedin_post_urn=attempt.linkedin_post_urn,
    )


async def _require_workspace_access(
    session: AsyncSession,
    current_user: CurrentUser,
    workspace_id: UUID,
    roles: set[WorkspaceRole] | None = None,
) -> None:
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
