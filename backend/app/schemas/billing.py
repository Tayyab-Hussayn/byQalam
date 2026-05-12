from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models.enums import SubscriptionStatus
from app.schemas.plan import PlanSeed
from app.schemas.usage import UsageSummaryResponse


class BillingCheckoutRequest(BaseModel):
    plan_slug: str = Field(min_length=1, max_length=80)
    success_url: str = Field(min_length=1, max_length=2048)
    cancel_url: str = Field(min_length=1, max_length=2048)


class BillingPortalRequest(BaseModel):
    return_url: str = Field(min_length=1, max_length=2048)


class BillingSessionResponse(BaseModel):
    url: str
    provider_session_id: str


class BillingSubscriptionResponse(BaseModel):
    workspace_id: UUID
    plan_slug: str | None = None
    status: SubscriptionStatus
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool


class BillingSummaryResponse(BaseModel):
    workspace_id: UUID
    plan: PlanSeed | None = None
    subscription: BillingSubscriptionResponse | None = None
    usage: UsageSummaryResponse
