from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.preferences import (
    ContentPreference,
    NicheProfile,
    VoiceProfile,
    WritingSample,
)
from app.db.models.user import User
from app.schemas.preferences import (
    ContentPreferenceUpsertRequest,
    VoiceProfileUpsertRequest,
    WritingSampleCreateRequest,
)


async def get_content_preferences(
    session: AsyncSession,
    workspace_id: UUID,
) -> ContentPreference | None:
    return await session.scalar(
        select(ContentPreference).where(ContentPreference.workspace_id == workspace_id)
    )


async def upsert_content_preferences(
    session: AsyncSession,
    workspace_id: UUID,
    payload: ContentPreferenceUpsertRequest,
) -> ContentPreference:
    preferences = await get_content_preferences(session, workspace_id)
    values = payload.model_dump()

    if preferences is None:
        preferences = ContentPreference(workspace_id=workspace_id, **values)
        session.add(preferences)
    else:
        for key, value in values.items():
            setattr(preferences, key, value)

    await session.commit()
    await session.refresh(preferences)
    return preferences


async def get_voice_profile(
    session: AsyncSession,
    workspace_id: UUID,
) -> VoiceProfile | None:
    return await session.scalar(
        select(VoiceProfile).where(VoiceProfile.workspace_id == workspace_id)
    )


async def upsert_voice_profile(
    session: AsyncSession,
    workspace_id: UUID,
    payload: VoiceProfileUpsertRequest,
) -> VoiceProfile:
    profile = await get_voice_profile(session, workspace_id)
    values = payload.model_dump()

    if profile is None:
        profile = VoiceProfile(workspace_id=workspace_id, **values)
        session.add(profile)
    else:
        for key, value in values.items():
            setattr(profile, key, value)

    profile.sample_count = await count_writing_samples(session, workspace_id)
    await session.commit()
    await session.refresh(profile)
    return profile


async def list_writing_samples(
    session: AsyncSession,
    workspace_id: UUID,
) -> list[WritingSample]:
    result = await session.execute(
        select(WritingSample)
        .where(WritingSample.workspace_id == workspace_id)
        .order_by(WritingSample.created_at.desc())
    )
    return list(result.scalars().all())


async def create_writing_sample(
    session: AsyncSession,
    workspace_id: UUID,
    user: User,
    payload: WritingSampleCreateRequest,
) -> WritingSample:
    sample = WritingSample(
        workspace_id=workspace_id,
        user_id=user.id,
        **payload.model_dump(),
    )
    session.add(sample)
    await session.flush()

    profile = await get_voice_profile(session, workspace_id)
    if profile is not None:
        profile.sample_count = await count_writing_samples(session, workspace_id)

    await session.commit()
    await session.refresh(sample)
    return sample


async def count_writing_samples(session: AsyncSession, workspace_id: UUID) -> int:
    return int(
        await session.scalar(
            select(func.count(WritingSample.id)).where(
                WritingSample.workspace_id == workspace_id
            )
        )
        or 0
    )


async def list_niche_profiles(session: AsyncSession) -> list[NicheProfile]:
    result = await session.execute(
        select(NicheProfile)
        .where(NicheProfile.is_active.is_(True))
        .order_by(NicheProfile.name.asc())
    )
    return list(result.scalars().all())
