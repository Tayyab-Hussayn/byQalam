from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.enums import UsageMetric
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class UsageLedger(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "usage_ledger"
    __table_args__ = (
        Index(
            "ix_usage_ledger_workspace_metric_period",
            "workspace_id",
            "metric",
            "period_start",
            "period_end",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    metric: Mapped[UsageMetric] = mapped_column(
        Enum(
            UsageMetric,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=80,
        ),
        index=True,
    )
    amount: Mapped[int] = mapped_column(default=1, nullable=False)
    period_start: Mapped[datetime] = mapped_column(index=True)
    period_end: Mapped[datetime] = mapped_column(index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
