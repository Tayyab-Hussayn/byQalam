from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import SubscriptionStatus
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class Subscription(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, index=True
    )
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("plans.id"), index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(
            SubscriptionStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255), unique=True
    )
    current_period_start: Mapped[datetime | None] = mapped_column()
    current_period_end: Mapped[datetime | None] = mapped_column()
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False, nullable=False)

    workspace = relationship("Workspace", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
