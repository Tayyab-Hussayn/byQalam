from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.models.enums import WorkspaceRole
from app.db.session import get_db_session
from app.schemas.generation import (
    GeneratePostRequest,
    GeneratePostResponse,
    RegeneratePostRequest,
)
from app.schemas.post import PostResponse
from app.services.generation import (
    generate_post_for_workspace,
    regenerate_post_for_workspace,
)
from app.services.posts import get_post
from app.services.workspaces import require_workspace_role

router = APIRouter(prefix="/workspaces/{workspace_id}/generation")

EDIT_ROLES = {WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.EDITOR}


@router.post("/generate-post", response_model=GeneratePostResponse)
async def generate_post_endpoint(
    workspace_id: UUID,
    payload: GeneratePostRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GeneratePostResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    post, run = await generate_post_for_workspace(
        session=session,
        workspace_id=workspace_id,
        user=current_user.user,
        payload=payload,
    )
    return GeneratePostResponse(
        post=PostResponse.model_validate(post),
        generation_run_id=run.id,
        quality_score=run.quality_score,
    )


@router.post("/posts/{post_id}/regenerate", response_model=GeneratePostResponse)
async def regenerate_post_endpoint(
    workspace_id: UUID,
    post_id: UUID,
    payload: RegeneratePostRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> GeneratePostResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    post = await get_post(session, workspace_id, post_id)
    if post is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "post_not_found", "message": "Post was not found."},
        )
    post, run = await regenerate_post_for_workspace(
        session,
        workspace_id,
        post,
        payload,
    )
    return GeneratePostResponse(
        post=PostResponse.model_validate(post),
        generation_run_id=run.id,
        quality_score=run.quality_score,
    )


async def _require_workspace_access(
    session: AsyncSession,
    current_user: CurrentUser,
    workspace_id: UUID,
) -> None:
    try:
        await require_workspace_role(
            session,
            current_user.user,
            workspace_id,
            EDIT_ROLES,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "workspace_forbidden",
                "message": "Workspace access is required.",
            },
        ) from exc
