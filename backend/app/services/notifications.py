from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.notification import Notification


async def create_failure_notification(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    title: str,
    body: str,
    entity_type: str,
    entity_id: str | None = None,
    severity: str = "error",
    metadata: dict | None = None,
) -> Notification:
    notification = Notification(
        workspace_id=workspace_id,
        severity=severity,
        title=title,
        body=body,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata or {},
    )
    session.add(notification)
    return notification
