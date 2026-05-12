import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ai import AiGenerationRun, PromptTemplate
from app.db.models.enums import GenerationStatus, PostSource, PostStatus, UsageMetric
from app.db.models.post import Post
from app.db.models.preferences import ContentPreference, VoiceProfile, WritingSample
from app.db.models.user import User
from app.schemas.generation import GeneratePostRequest, RegeneratePostRequest
from app.schemas.post import PostCreateRequest, PostUpdateRequest
from app.services.ai.factory import get_generation_provider
from app.services.ai.providers import GenerationContext
from app.services.audit import record_audit_event
from app.services.notifications import create_failure_notification
from app.services.posts import create_post, update_post
from app.services.usage import assert_quota_available, record_usage


async def generate_post_for_workspace(
    session: AsyncSession,
    workspace_id: UUID,
    user: User,
    payload: GeneratePostRequest,
) -> tuple[Post, AiGenerationRun]:
    await assert_quota_available(session, workspace_id, UsageMetric.AI_GENERATION)
    context = await build_generation_context(session, workspace_id, payload)
    provider = get_generation_provider()
    template = await get_active_prompt_template(session)
    started = time.perf_counter()

    run = AiGenerationRun(
        workspace_id=workspace_id,
        status=GenerationStatus.RUNNING,
        provider=provider.provider_name,
        model=provider.model_name,
        prompt_template_name=template.name if template else None,
        prompt_template_version=template.version if template else None,
        input_json={**payload.model_dump(), "context": context.__dict__},
        output_json={},
    )
    session.add(run)
    await session.flush()

    try:
        generated = await provider.generate_post(context)
        post = await create_post(
            session=session,
            workspace_id=workspace_id,
            user=user,
            payload=PostCreateRequest(
                body=generated.body,
                title_internal=payload.title_internal or payload.prompt[:120],
                source=PostSource.AI,
                niche_slug=context.niche_slug,
                hashtags=generated.hashtags,
                first_comment=generated.first_comment,
            ),
        )
        post.status = PostStatus.GENERATED
        run.post_id = post.id
        run.status = GenerationStatus.SUCCEEDED
        run.output_json = {
            "body": generated.body,
            "hashtags": generated.hashtags,
            "first_comment": generated.first_comment,
        }
        run.quality_score = generated.quality_score
        run.tokens_input = generated.tokens_input
        run.tokens_output = generated.tokens_output
        run.estimated_cost_cents = generated.estimated_cost_cents
        run.latency_ms = int((time.perf_counter() - started) * 1000)
        await record_usage(session, workspace_id, UsageMetric.AI_GENERATION)
        await record_audit_event(
            session,
            action="generation.succeeded",
            entity_type="ai_generation_run",
            entity_id=str(run.id),
            workspace_id=workspace_id,
            actor_user_id=user.id,
            metadata={"post_id": str(post.id), "provider": provider.provider_name},
        )
        await session.commit()
        await session.refresh(post)
        await session.refresh(run)
        return post, run
    except Exception as exc:
        run.status = GenerationStatus.FAILED
        run.failure_reason = str(exc)[:500]
        run.latency_ms = int((time.perf_counter() - started) * 1000)
        await create_failure_notification(
            session,
            workspace_id=workspace_id,
            title="AI generation failed",
            body=run.failure_reason or "The content generation request failed.",
            entity_type="ai_generation_run",
            entity_id=str(run.id),
            metadata={
                "provider": provider.provider_name,
                "model": provider.model_name,
                "error": run.failure_reason,
            },
        )
        await record_audit_event(
            session,
            action="generation.failed",
            entity_type="ai_generation_run",
            entity_id=str(run.id),
            workspace_id=workspace_id,
            actor_user_id=user.id,
            metadata={"error": str(exc)[:500]},
        )
        await session.commit()
        raise


async def regenerate_post_for_workspace(
    session: AsyncSession,
    workspace_id: UUID,
    post: Post,
    payload: RegeneratePostRequest,
) -> tuple[Post, AiGenerationRun]:
    await assert_quota_available(session, workspace_id, UsageMetric.AI_REGENERATION)
    request = GeneratePostRequest(
        prompt=payload.instruction or f"Regenerate this post: {payload.reason}",
        tone=None,
        niche_slug=post.niche_slug,
        title_internal=post.title_internal,
    )
    context = await build_generation_context(session, workspace_id, request)
    provider = get_generation_provider()
    started = time.perf_counter()
    run = AiGenerationRun(
        workspace_id=workspace_id,
        post_id=post.id,
        status=GenerationStatus.RUNNING,
        provider=provider.provider_name,
        model=provider.model_name,
        input_json={
            **request.model_dump(),
            "regeneration_reason": payload.reason,
            "context": context.__dict__,
        },
        output_json={},
    )
    session.add(run)
    await session.flush()
    generated = await provider.generate_post(context)
    updated = await update_post(
        session,
        post,
        PostUpdateRequest(
            body=generated.body,
            title_internal=post.title_internal,
            hashtags=generated.hashtags,
            first_comment=generated.first_comment,
            change_reason=f"regenerated:{payload.reason}",
        ),
    )
    updated.status = PostStatus.GENERATED
    run.status = GenerationStatus.SUCCEEDED
    run.output_json = {
        "body": generated.body,
        "hashtags": generated.hashtags,
        "first_comment": generated.first_comment,
    }
    run.quality_score = generated.quality_score
    run.tokens_input = generated.tokens_input
    run.tokens_output = generated.tokens_output
    run.estimated_cost_cents = generated.estimated_cost_cents
    run.latency_ms = int((time.perf_counter() - started) * 1000)
    await record_usage(session, workspace_id, UsageMetric.AI_REGENERATION)
    await record_audit_event(
        session,
        action="generation.regenerated",
        entity_type="ai_generation_run",
        entity_id=str(run.id),
        workspace_id=workspace_id,
        metadata={"post_id": str(post.id), "provider": provider.provider_name},
    )
    await session.commit()
    await session.refresh(updated)
    await session.refresh(run)
    return updated, run


async def build_generation_context(
    session: AsyncSession,
    workspace_id: UUID,
    payload: GeneratePostRequest,
) -> GenerationContext:
    preferences = await session.scalar(
        select(ContentPreference).where(ContentPreference.workspace_id == workspace_id)
    )
    voice = await session.scalar(
        select(VoiceProfile).where(VoiceProfile.workspace_id == workspace_id)
    )
    samples = await session.execute(
        select(WritingSample.body)
        .where(WritingSample.workspace_id == workspace_id)
        .order_by(WritingSample.created_at.desc())
        .limit(3)
    )
    niche_slug = payload.niche_slug
    if niche_slug is None and preferences is not None:
        niche_slug = preferences.niche_slug

    return GenerationContext(
        prompt=payload.prompt,
        niche_slug=niche_slug,
        target_audience=preferences.target_audience if preferences else None,
        tone=payload.tone or (preferences.tone if preferences else None),
        language=preferences.language if preferences else "en",
        content_goals=preferences.content_goals if preferences else [],
        topics_to_avoid=preferences.topics_to_avoid if preferences else [],
        voice_traits=voice.traits if voice else [],
        writing_sample_snippets=[body[:500] for body in samples.scalars().all()],
    )


async def get_active_prompt_template(
    session: AsyncSession,
) -> PromptTemplate | None:
    return await session.scalar(
        select(PromptTemplate)
        .where(
            PromptTemplate.name == "linkedin_post",
            PromptTemplate.is_active.is_(True),
        )
        .order_by(PromptTemplate.created_at.desc())
    )
