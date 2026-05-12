import hashlib
import hmac
import json
from datetime import datetime
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.enums import SubscriptionStatus
from app.db.models.plan import Plan
from app.db.models.subscription import Subscription
from app.db.models.workspace import Workspace
from app.schemas.billing import BillingCheckoutRequest, BillingPortalRequest
from app.schemas.plan import PlanQuota, PlanSeed
from app.services.audit import record_audit_event

STRIPE_API_BASE = "https://api.stripe.com/v1"


class BillingConfigError(RuntimeError):
    pass


class BillingWebhookError(RuntimeError):
    pass


def _require_stripe_secret() -> str:
    if not settings.stripe_secret_key:
        raise BillingConfigError("STRIPE_SECRET_KEY is not configured")
    return settings.stripe_secret_key


async def build_billing_summary(
    session: AsyncSession,
    workspace_id: UUID,
):
    workspace = await session.get(Workspace, workspace_id)
    if workspace is None:
        raise PermissionError("Workspace not found")
    subscription = await session.scalar(
        select(Subscription).where(Subscription.workspace_id == workspace_id)
    )
    plan = None
    if subscription is not None:
        plan_row = await session.get(Plan, subscription.plan_id)
        if plan_row is not None:
            plan = PlanSeed(
                slug=plan_row.slug,
                name=plan_row.name,
                sort_order=plan_row.sort_order,
                stripe_price_id=plan_row.stripe_price_id,
                quotas=PlanQuota.model_validate(plan_row.quotas),
            )
    elif (plan_row := await session.scalar(select(Plan).where(Plan.slug == "free"))):
        plan = PlanSeed(
                slug=plan_row.slug,
                name=plan_row.name,
                sort_order=plan_row.sort_order,
                stripe_price_id=plan_row.stripe_price_id,
                quotas=PlanQuota.model_validate(plan_row.quotas),
            )
    return workspace, plan, subscription


async def create_checkout_session(
    session: AsyncSession,
    workspace_id: UUID,
    payload: BillingCheckoutRequest,
) -> tuple[str, str]:
    secret = _require_stripe_secret()
    plan = await session.scalar(select(Plan).where(Plan.slug == payload.plan_slug))
    if plan is None or not plan.stripe_price_id:
        raise BillingConfigError("Requested plan is not configured with a Stripe price")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{STRIPE_API_BASE}/checkout/sessions",
            data={
                "mode": "subscription",
                "success_url": payload.success_url,
                "cancel_url": payload.cancel_url,
                "line_items[0][price]": plan.stripe_price_id,
                "line_items[0][quantity]": 1,
                "client_reference_id": str(workspace_id),
                "metadata[workspace_id]": str(workspace_id),
                "metadata[plan_slug]": plan.slug,
            },
            auth=(secret, ""),
        )
    if response.status_code >= 400:
        raise BillingConfigError(response.text[:1000])
    data = response.json()
    await record_audit_event(
        session,
        action="billing.checkout.created",
        entity_type="stripe_checkout_session",
        entity_id=data["id"],
        workspace_id=workspace_id,
        metadata={"plan_slug": plan.slug},
    )
    await session.commit()
    return data["url"], data["id"]


async def create_portal_session(
    session: AsyncSession,
    workspace_id: UUID,
    payload: BillingPortalRequest,
) -> tuple[str, str]:
    secret = _require_stripe_secret()
    subscription = await session.scalar(
        select(Subscription).where(Subscription.workspace_id == workspace_id)
    )
    if subscription is None or not subscription.stripe_customer_id:
        raise BillingConfigError("Workspace has no Stripe customer id")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{STRIPE_API_BASE}/billing_portal/sessions",
            data={
                "customer": subscription.stripe_customer_id,
                "return_url": payload.return_url,
            },
            auth=(secret, ""),
        )
    if response.status_code >= 400:
        raise BillingConfigError(response.text[:1000])
    data = response.json()
    await record_audit_event(
        session,
        action="billing.portal.created",
        entity_type="stripe_billing_portal_session",
        entity_id=data["id"],
        workspace_id=workspace_id,
    )
    await session.commit()
    return data["url"], data["id"]


def verify_stripe_signature(payload: bytes, header: str) -> None:
    secret = settings.stripe_webhook_secret
    if not secret:
        raise BillingConfigError("STRIPE_WEBHOOK_SECRET is not configured")

    parts = dict(item.split("=", 1) for item in header.split(",") if "=" in item)
    timestamp = parts.get("t")
    signature = parts.get("v1")
    if not timestamp or not signature:
        raise BillingWebhookError("Malformed Stripe signature header")

    signed_payload = f"{timestamp}.{payload.decode()}".encode()
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise BillingWebhookError("Invalid Stripe webhook signature")


async def handle_stripe_event(
    session: AsyncSession,
    payload: bytes,
    signature_header: str,
) -> dict[str, str]:
    verify_stripe_signature(payload, signature_header)
    event = json.loads(payload.decode())
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        await sync_checkout_session(session, data)
    elif event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        await sync_subscription(session, data)

    await record_audit_event(
        session,
        action="billing.webhook.received",
        entity_type="stripe_event",
        entity_id=event.get("id"),
        metadata={"type": event_type},
    )
    await session.commit()
    return {"status": "processed", "type": event_type}


async def sync_checkout_session(session: AsyncSession, data: dict) -> None:
    workspace_id = data.get("metadata", {}).get("workspace_id")
    plan_slug = data.get("metadata", {}).get("plan_slug")
    if not workspace_id or not plan_slug:
        raise BillingWebhookError("Checkout session metadata is incomplete")
    plan = await session.scalar(select(Plan).where(Plan.slug == plan_slug))
    if plan is None:
        raise BillingWebhookError("Plan not found for checkout session")
    workspace_uuid = UUID(workspace_id)
    subscription = await session.scalar(
        select(Subscription).where(Subscription.workspace_id == workspace_uuid)
    )
    if subscription is None:
        subscription = Subscription(
            workspace_id=workspace_uuid,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
        )
        session.add(subscription)
    subscription.plan_id = plan.id
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.stripe_customer_id = data.get("customer")
    subscription.stripe_subscription_id = data.get("subscription")


async def sync_subscription(session: AsyncSession, data: dict) -> None:
    stripe_subscription_id = data.get("id")
    customer_id = data.get("customer")
    subscription = await session.scalar(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
    )
    if subscription is None and customer_id:
        subscription = await session.scalar(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
    if subscription is None:
        return
    subscription.status = SubscriptionStatus(data.get("status", "active"))
    subscription.cancel_at_period_end = data.get("cancel_at_period_end", False)
    current_period_start = data.get("current_period_start")
    current_period_end = data.get("current_period_end")
    subscription.current_period_start = datetime.utcfromtimestamp(
        current_period_start
    ) if current_period_start else None
    subscription.current_period_end = datetime.utcfromtimestamp(
        current_period_end
    ) if current_period_end else None
    subscription.stripe_customer_id = customer_id or subscription.stripe_customer_id
    subscription.stripe_subscription_id = (
        stripe_subscription_id or subscription.stripe_subscription_id
    )
