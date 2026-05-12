from sqlalchemy import JSON, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import PlanInterval
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class Plan(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "plans"

    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(500))
    interval: Mapped[PlanInterval] = mapped_column(
        Enum(
            PlanInterval,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=20,
        ),
        default=PlanInterval.MONTH,
        nullable=False,
    )
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    quotas: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    is_public: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")
