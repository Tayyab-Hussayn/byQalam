import asyncio
from datetime import datetime
from uuid import UUID

from app.db.models.user import User
from app.db.session import async_session_factory
from app.schemas.generation import GeneratePostRequest
from app.services.dead_letters import record_dead_letter
from app.services.generation import generate_post_for_workspace
from app.services.publishing import publish_due_scheduled_posts
from app.workers.celery_app import celery_app


@celery_app.task(
    name="qalam.publish_due_scheduled_posts",
    bind=True,
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def publish_due_scheduled_posts_task(self, limit: int = 25) -> dict[str, int]:
    try:
        return asyncio.run(_publish_due_scheduled_posts(limit))
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc) from exc
        asyncio.run(
            _record_dead_letter(
                task_name=self.name,
                task_id=self.request.id or "",
                payload={"limit": limit},
                error={"error": str(exc), "type": exc.__class__.__name__},
                retries=self.request.retries,
                max_retries=self.max_retries,
            )
        )
        raise


async def _publish_due_scheduled_posts(limit: int) -> dict[str, int]:
    async with async_session_factory() as session:
        result = await publish_due_scheduled_posts(
            session,
            due_at=datetime.utcnow(),
            limit=limit,
        )
    return {
        "scanned": result.scanned,
        "published": result.published,
        "failed": result.failed,
    }


@celery_app.task(
    name="qalam.generate_post_for_workspace",
    bind=True,
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def generate_post_for_workspace_task(
    self,
    workspace_id: str,
    user_id: str,
    prompt: str,
    tone: str | None = None,
    niche_slug: str | None = None,
    title_internal: str | None = None,
) -> dict[str, str]:
    try:
        return asyncio.run(
            _generate_post_for_workspace(
                UUID(workspace_id),
                UUID(user_id),
                prompt,
                tone,
                niche_slug,
                title_internal,
            )
        )
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc) from exc
        asyncio.run(
            _record_dead_letter(
                task_name=self.name,
                task_id=self.request.id or "",
                workspace_id=UUID(workspace_id),
                entity_type="workspace",
                entity_id=workspace_id,
                payload={
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "prompt": prompt,
                    "tone": tone,
                    "niche_slug": niche_slug,
                    "title_internal": title_internal,
                },
                error={"error": str(exc), "type": exc.__class__.__name__},
                retries=self.request.retries,
                max_retries=self.max_retries,
            )
        )
        raise


async def _generate_post_for_workspace(
    workspace_id: UUID,
    user_id: UUID,
    prompt: str,
    tone: str | None,
    niche_slug: str | None,
    title_internal: str | None,
) -> dict[str, str]:
    async with async_session_factory() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise ValueError("User was not found")

        post, run = await generate_post_for_workspace(
            session=session,
            workspace_id=workspace_id,
            user=user,
            payload=GeneratePostRequest(
                prompt=prompt,
                tone=tone,
                niche_slug=niche_slug,
                title_internal=title_internal,
            ),
        )

    return {
        "post_id": str(post.id),
        "generation_run_id": str(run.id),
    }


async def _record_dead_letter(
    *,
    task_name: str,
    task_id: str,
    payload: dict,
    error: dict,
    workspace_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    retries: int = 0,
    max_retries: int | None = None,
) -> None:
    async with async_session_factory() as session:
        await record_dead_letter(
            session,
            task_name=task_name,
            task_id=task_id,
            workspace_id=workspace_id,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            error=error,
            retries=retries,
            max_retries=max_retries,
        )
