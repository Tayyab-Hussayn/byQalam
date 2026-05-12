from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.dead_letter import DeadLetterJob


async def record_dead_letter(
    session: AsyncSession,
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
) -> DeadLetterJob:
    dead_letter = DeadLetterJob(
        task_name=task_name,
        task_id=task_id,
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id,
        retries=retries,
        max_retries=max_retries,
        payload_json=payload,
        error_json=error,
    )
    session.add(dead_letter)
    await session.commit()
    await session.refresh(dead_letter)
    return dead_letter
