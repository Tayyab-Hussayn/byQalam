from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import LinkedinConnectionStatus, PostStatus
from app.db.models.linkedin import LinkedinConnection
from app.db.models.post import Post, ScheduledPost
from app.services.linkedin import publish_text_post
from app.services.notifications import create_failure_notification


@dataclass(frozen=True)
class PublishingResult:
    scanned: int
    published: int
    failed: int


async def claim_due_scheduled_posts(
    session: AsyncSession,
    due_at: datetime,
    limit: int = 25,
) -> list[tuple[ScheduledPost, Post]]:
    result = await session.execute(
        select(ScheduledPost, Post)
        .join(Post, ScheduledPost.post_id == Post.id)
        .where(
            ScheduledPost.status == PostStatus.SCHEDULED,
            ScheduledPost.scheduled_for <= due_at,
            Post.status == PostStatus.SCHEDULED,
        )
        .order_by(ScheduledPost.scheduled_for.asc())
        .limit(limit)
    )
    rows = list(result.all())
    for scheduled, post in rows:
        scheduled.status = PostStatus.PUBLISHING
        post.status = PostStatus.PUBLISHING
    if rows:
        await session.commit()
    return rows


async def publish_due_scheduled_posts(
    session: AsyncSession,
    due_at: datetime | None = None,
    limit: int = 25,
) -> PublishingResult:
    due_at = due_at or datetime.utcnow()
    claimed = await claim_due_scheduled_posts(session, due_at, limit)
    published = 0
    failed = 0

    for scheduled, post in claimed:
        connection = await select_connection_for_post(session, post)
        if connection is None:
            post.status = PostStatus.FAILED
            scheduled.status = PostStatus.FAILED
            post.failure_reason = "No active LinkedIn connection found for post target."
            await create_failure_notification(
                session,
                workspace_id=post.workspace_id,
                title="Scheduled post could not publish",
                body=post.failure_reason,
                entity_type="post",
                entity_id=str(post.id),
                metadata={"scheduled_post_id": str(scheduled.id)},
            )
            await session.commit()
            failed += 1
            continue

        attempt = await publish_text_post(session, post, connection)
        scheduled.status = post.status
        await session.commit()
        if attempt.linkedin_post_urn:
            published += 1
        else:
            failed += 1

    return PublishingResult(
        scanned=len(claimed),
        published=published,
        failed=failed,
    )


async def select_connection_for_post(
    session: AsyncSession,
    post: Post,
) -> LinkedinConnection | None:
    query = select(LinkedinConnection).where(
        LinkedinConnection.workspace_id == post.workspace_id,
        LinkedinConnection.status == LinkedinConnectionStatus.CONNECTED,
    )
    if post.linkedin_target_urn:
        query = query.where(LinkedinConnection.target_urn == post.linkedin_target_urn)
    query = query.order_by(LinkedinConnection.created_at.desc())
    return await session.scalar(query)
