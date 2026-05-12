from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import PostStatus, UsageMetric
from app.db.models.post import Post, PostVersion, ScheduledPost
from app.db.models.user import User
from app.schemas.post import (
    PostCreateRequest,
    PostRejectRequest,
    PostScheduleRequest,
    PostUpdateRequest,
)
from app.services.audit import record_audit_event
from app.services.usage import assert_quota_available, record_usage


async def list_posts(
    session: AsyncSession,
    workspace_id: UUID,
    status: PostStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Post]:
    query = select(Post).where(Post.workspace_id == workspace_id)
    if status is not None:
        query = query.where(Post.status == status)
    result = await session.execute(
        query.order_by(Post.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_post(
    session: AsyncSession,
    workspace_id: UUID,
    post_id: UUID,
) -> Post | None:
    return await session.scalar(
        select(Post).where(Post.workspace_id == workspace_id, Post.id == post_id)
    )


async def create_post(
    session: AsyncSession,
    workspace_id: UUID,
    user: User,
    payload: PostCreateRequest,
) -> Post:
    post = Post(
        workspace_id=workspace_id,
        author_user_id=user.id,
        status=PostStatus.DRAFT,
        **payload.model_dump(),
    )
    session.add(post)
    await session.flush()
    await add_post_version(session, post, "initial")
    await record_audit_event(
        session,
        action="post.created",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=workspace_id,
        actor_user_id=user.id,
        metadata={"source": post.source.value},
    )
    await session.commit()
    await session.refresh(post)
    return post


async def update_post(
    session: AsyncSession,
    post: Post,
    payload: PostUpdateRequest,
) -> Post:
    post.body = payload.body
    post.title_internal = payload.title_internal
    post.hashtags = payload.hashtags
    post.first_comment = payload.first_comment
    if post.status in {PostStatus.REJECTED, PostStatus.FAILED, PostStatus.CANCELLED}:
        post.status = PostStatus.DRAFT
    await add_post_version(session, post, payload.change_reason)
    await record_audit_event(
        session,
        action="post.updated",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=post.workspace_id,
        metadata={"change_reason": payload.change_reason},
    )
    await session.commit()
    await session.refresh(post)
    return post


async def approve_post(session: AsyncSession, post: Post) -> Post:
    post.status = PostStatus.APPROVED
    post.rejection_reason = None
    await record_audit_event(
        session,
        action="post.approved",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=post.workspace_id,
    )
    await session.commit()
    await session.refresh(post)
    return post


async def reject_post(
    session: AsyncSession,
    post: Post,
    payload: PostRejectRequest,
) -> Post:
    post.status = PostStatus.REJECTED
    post.rejection_reason = payload.reason
    await record_audit_event(
        session,
        action="post.rejected",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=post.workspace_id,
        metadata={"reason": payload.reason},
    )
    await session.commit()
    await session.refresh(post)
    return post


async def schedule_post(
    session: AsyncSession,
    post: Post,
    payload: PostScheduleRequest,
) -> Post:
    await assert_quota_available(
        session,
        post.workspace_id,
        UsageMetric.SCHEDULED_POST,
    )
    post.status = PostStatus.SCHEDULED
    post.scheduled_for = payload.scheduled_for.replace(tzinfo=None)
    post.timezone = payload.timezone
    post.linkedin_target_type = payload.linkedin_target_type
    post.linkedin_target_urn = payload.linkedin_target_urn

    scheduled = await session.scalar(
        select(ScheduledPost).where(ScheduledPost.post_id == post.id)
    )
    if scheduled is None:
        session.add(
            ScheduledPost(
                workspace_id=post.workspace_id,
                post_id=post.id,
                status=PostStatus.SCHEDULED,
                scheduled_for=post.scheduled_for,
                timezone=post.timezone,
            )
        )
    else:
        scheduled.status = PostStatus.SCHEDULED
        scheduled.scheduled_for = post.scheduled_for
        scheduled.timezone = post.timezone

    await record_usage(session, post.workspace_id, UsageMetric.SCHEDULED_POST)
    await record_audit_event(
        session,
        action="post.scheduled",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=post.workspace_id,
        metadata={
            "scheduled_for": post.scheduled_for.isoformat(),
            "timezone": post.timezone,
        },
    )
    await session.commit()
    await session.refresh(post)
    return post


async def cancel_scheduled_post(session: AsyncSession, post: Post) -> Post:
    post.status = PostStatus.CANCELLED
    scheduled = await session.scalar(
        select(ScheduledPost).where(ScheduledPost.post_id == post.id)
    )
    if scheduled is not None:
        scheduled.status = PostStatus.CANCELLED
    await record_audit_event(
        session,
        action="post.cancelled",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=post.workspace_id,
    )
    await session.commit()
    await session.refresh(post)
    return post


async def delete_post(session: AsyncSession, post: Post) -> None:
    await session.delete(post)
    await record_audit_event(
        session,
        action="post.deleted",
        entity_type="post",
        entity_id=str(post.id),
        workspace_id=post.workspace_id,
        metadata={"status": post.status.value},
    )
    await session.commit()


async def list_post_versions(session: AsyncSession, post: Post) -> list[PostVersion]:
    result = await session.execute(
        select(PostVersion)
        .where(PostVersion.post_id == post.id)
        .order_by(PostVersion.version_number.desc())
    )
    return list(result.scalars().all())


async def add_post_version(
    session: AsyncSession,
    post: Post,
    change_reason: str | None,
) -> PostVersion:
    next_version = (
        await session.scalar(
            select(func.count(PostVersion.id)).where(PostVersion.post_id == post.id)
        )
        or 0
    ) + 1
    version = PostVersion(
        post_id=post.id,
        version_number=next_version,
        body=post.body,
        hashtags=post.hashtags,
        first_comment=post.first_comment,
        change_reason=change_reason,
    )
    session.add(version)
    return version
