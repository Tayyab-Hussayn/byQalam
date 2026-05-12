from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import request_id_context
from app.db.models.audit import AuditLog


async def record_audit_event(
    session: AsyncSession,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    workspace_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    metadata: dict | None = None,
) -> None:
    session.add(
        AuditLog(
            workspace_id=workspace_id,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            request_id=request_id_context.get() or None,
            metadata_json=metadata or {},
        )
    )
