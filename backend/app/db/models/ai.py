from uuid import UUID

from sqlalchemy import JSON, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import GenerationStatus
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class PromptTemplate(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(String(120), index=True)
    version: Mapped[str] = mapped_column(String(40), index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    system_prompt: Mapped[str] = mapped_column(Text)
    user_prompt_template: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class AiGenerationRun(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_generation_runs"
    __table_args__ = (
        Index(
            "ix_ai_generation_runs_workspace_created",
            "workspace_id",
            "created_at",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    post_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("posts.id", ondelete="SET NULL"),
        index=True,
    )
    status: Mapped[GenerationStatus] = mapped_column(
        Enum(
            GenerationStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=GenerationStatus.QUEUED,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(120))
    prompt_template_name: Mapped[str | None] = mapped_column(String(120))
    prompt_template_version: Mapped[str | None] = mapped_column(String(40))
    input_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    quality_score: Mapped[int | None] = mapped_column()
    tokens_input: Mapped[int | None] = mapped_column()
    tokens_output: Mapped[int | None] = mapped_column()
    estimated_cost_cents: Mapped[int | None] = mapped_column()
    latency_ms: Mapped[int | None] = mapped_column()
    failure_reason: Mapped[str | None] = mapped_column(String(500))

    post = relationship("Post")
