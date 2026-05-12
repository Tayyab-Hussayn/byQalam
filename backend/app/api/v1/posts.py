from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.models.enums import PostStatus, WorkspaceRole
from app.db.models.post import Post
from app.db.session import get_db_session
from app.schemas.media import PostMediaCreateRequest, PostMediaResponse
from app.schemas.post import (
    PostCreateRequest,
    PostListResponse,
    PostRejectRequest,
    PostResponse,
    PostScheduleRequest,
    PostUpdateRequest,
    PostVersionListResponse,
    PostVersionResponse,
)
from app.services.media import attach_post_media
from app.services.posts import (
    approve_post,
    cancel_scheduled_post,
    create_post,
    delete_post,
    get_post,
    list_post_versions,
    list_posts,
    reject_post,
    schedule_post,
    update_post,
)
from app.services.workspaces import require_workspace_role

router = APIRouter(prefix="/workspaces/{workspace_id}/posts")

EDIT_ROLES = {WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.EDITOR}


@router.get("", response_model=PostListResponse)
async def read_posts(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status: PostStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PostListResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    posts = await list_posts(session, workspace_id, status, limit, offset)
    return PostListResponse(posts=[PostResponse.model_validate(post) for post in posts])


@router.post("", response_model=PostResponse, status_code=201)
async def create_post_endpoint(
    workspace_id: UUID,
    payload: PostCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await create_post(session, workspace_id, current_user.user, payload)
    return PostResponse.model_validate(post)


@router.post(
    "/{post_id}/media",
    response_model=PostMediaResponse,
    status_code=201,
)
async def add_post_media_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    payload: PostMediaCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostMediaResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    media = await attach_post_media(session, post, payload)
    return PostMediaResponse.model_validate(media)


@router.get("/{post_id}", response_model=PostResponse)
async def read_post(
    workspace_id: UUID,
    post_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    post = await _get_existing_post(session, workspace_id, post_id)
    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    payload: PostUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    post = await update_post(session, post, payload)
    return PostResponse.model_validate(post)


@router.get("/{post_id}/versions", response_model=PostVersionListResponse)
async def read_post_versions(
    workspace_id: UUID,
    post_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostVersionListResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    post = await _get_existing_post(session, workspace_id, post_id)
    versions = await list_post_versions(session, post)
    return PostVersionListResponse(
        versions=[PostVersionResponse.model_validate(version) for version in versions]
    )


@router.post("/{post_id}/approve", response_model=PostResponse)
async def approve_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    return PostResponse.model_validate(await approve_post(session, post))


@router.post("/{post_id}/reject", response_model=PostResponse)
async def reject_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    payload: PostRejectRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    return PostResponse.model_validate(await reject_post(session, post, payload))


@router.post("/{post_id}/schedule", response_model=PostResponse)
async def schedule_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    payload: PostScheduleRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    if post.status not in {PostStatus.APPROVED, PostStatus.SCHEDULED}:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "post_not_approved",
                "message": "Only approved posts can be scheduled.",
            },
        )
    return PostResponse.model_validate(await schedule_post(session, post, payload))


@router.post("/{post_id}/cancel", response_model=PostResponse)
async def cancel_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PostResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    return PostResponse.model_validate(await cancel_scheduled_post(session, post))


@router.delete("/{post_id}", status_code=204)
async def delete_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    post = await _get_existing_post(session, workspace_id, post_id)
    if post.status not in {
        PostStatus.DRAFT,
        PostStatus.GENERATED,
        PostStatus.NEEDS_REVIEW,
        PostStatus.REJECTED,
        PostStatus.FAILED,
        PostStatus.CANCELLED,
    }:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "post_not_deletable",
                "message": "Only draft or pre-publish posts can be deleted.",
            },
        )
    await delete_post(session, post)
    return Response(status_code=204)


async def _get_existing_post(
    session: AsyncSession,
    workspace_id: UUID,
    post_id: UUID,
) -> Post:
    post = await get_post(session, workspace_id, post_id)
    if post is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "post_not_found", "message": "Post was not found."},
        )
    return post


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
