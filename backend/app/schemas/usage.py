from datetime import datetime

from pydantic import BaseModel

from app.db.models.enums import UsageMetric


class UsageItemResponse(BaseModel):
    metric: UsageMetric
    used: int
    limit: int | None


class UsageSummaryResponse(BaseModel):
    plan_slug: str
    period_start: datetime
    period_end: datetime
    items: list[UsageItemResponse]
