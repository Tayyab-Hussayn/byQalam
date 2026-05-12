from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.models.enums import WorkspaceRole
from app.db.session import get_db_session
from app.schemas.preferences import (
    ContentPreferenceResponse,
    ContentPreferenceUpsertRequest,
    NicheProfileListResponse,
    NicheProfileResponse,
    VoiceProfileResponse,
    VoiceProfileUpsertRequest,
    WritingSampleCreateRequest,
    WritingSampleListResponse,
    WritingSampleResponse,
)
from app.services.preferences import (
    create_writing_sample,
    get_content_preferences,
    get_voice_profile,
    list_niche_profiles,
    list_writing_samples,
    upsert_content_preferences,
    upsert_voice_profile,
)
from app.services.workspaces import require_workspace_role

router = APIRouter()

EDIT_ROLES = {WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.EDITOR}


@router.get("/niches", response_model=NicheProfileListResponse)
async def list_niches(
    _current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> NicheProfileListResponse:
    niches = await list_niche_profiles(session)
    return NicheProfileListResponse(
        niches=[NicheProfileResponse.model_validate(niche) for niche in niches]
    )


@router.get(
    "/workspaces/{workspace_id}/preferences",
    response_model=ContentPreferenceResponse | None,
)
async def read_content_preferences(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ContentPreferenceResponse | None:
    await _require_workspace_access(session, current_user, workspace_id)
    preferences = await get_content_preferences(session, workspace_id)
    return (
        ContentPreferenceResponse.model_validate(preferences)
        if preferences is not None
        else None
    )


@router.put(
    "/workspaces/{workspace_id}/preferences",
    response_model=ContentPreferenceResponse,
)
async def save_content_preferences(
    workspace_id: UUID,
    payload: ContentPreferenceUpsertRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ContentPreferenceResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    preferences = await upsert_content_preferences(session, workspace_id, payload)
    return ContentPreferenceResponse.model_validate(preferences)


@router.get(
    "/workspaces/{workspace_id}/voice-profile",
    response_model=VoiceProfileResponse | None,
)
async def read_voice_profile(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> VoiceProfileResponse | None:
    await _require_workspace_access(session, current_user, workspace_id)
    profile = await get_voice_profile(session, workspace_id)
    return VoiceProfileResponse.model_validate(profile) if profile is not None else None


@router.put(
    "/workspaces/{workspace_id}/voice-profile",
    response_model=VoiceProfileResponse,
)
async def save_voice_profile(
    workspace_id: UUID,
    payload: VoiceProfileUpsertRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> VoiceProfileResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    profile = await upsert_voice_profile(session, workspace_id, payload)
    return VoiceProfileResponse.model_validate(profile)


@router.get(
    "/workspaces/{workspace_id}/writing-samples",
    response_model=WritingSampleListResponse,
)
async def read_writing_samples(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WritingSampleListResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    samples = await list_writing_samples(session, workspace_id)
    return WritingSampleListResponse(
        samples=[WritingSampleResponse.model_validate(sample) for sample in samples]
    )


@router.post(
    "/workspaces/{workspace_id}/writing-samples",
    response_model=WritingSampleResponse,
    status_code=201,
)
async def add_writing_sample(
    workspace_id: UUID,
    payload: WritingSampleCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WritingSampleResponse:
    await _require_workspace_access(session, current_user, workspace_id, EDIT_ROLES)
    sample = await create_writing_sample(
        session=session,
        workspace_id=workspace_id,
        user=current_user.user,
        payload=payload,
    )
    return WritingSampleResponse.model_validate(sample)


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
