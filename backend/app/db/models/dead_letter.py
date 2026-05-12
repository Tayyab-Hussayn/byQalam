from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class DeadLetterJob(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dead_letter_jobs"
    __table_args__ = (
        Index("ix_dead_letter_jobs_task_name_created", "task_name", "created_at"),
        Index("ix_dead_letter_jobs_workspace_created", "workspace_id", "created_at"),
        Index("ix_dead_letter_jobs_entity_type_entity_id", "entity_type", "entity_id"),
    )

    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    workspace_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"),
        index=True,
    )
    entity_type: Mapped[str | None] = mapped_column(String(120))
    entity_id: Mapped[str | None] = mapped_column(String(255))
    retries: Mapped[int] = mapped_column(default=0, nullable=False)
    max_retries: Mapped[int | None] = mapped_column()
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
