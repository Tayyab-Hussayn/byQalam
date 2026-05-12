from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.models.enums import WorkspaceRole
from app.db.session import get_db_session
from app.schemas.billing import (
    BillingCheckoutRequest,
    BillingPortalRequest,
    BillingSessionResponse,
    BillingSubscriptionResponse,
    BillingSummaryResponse,
)
from app.schemas.usage import UsageItemResponse, UsageSummaryResponse
from app.services.billing import (
    BillingConfigError,
    BillingWebhookError,
    build_billing_summary,
    create_checkout_session,
    create_portal_session,
    handle_stripe_event,
)
from app.services.usage import build_usage_summary
from app.services.workspaces import require_workspace_role

router = APIRouter(prefix="/billing")


@router.get(
    "/workspaces/{workspace_id}",
    response_model=BillingSummaryResponse,
)
async def read_billing_summary(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BillingSummaryResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    workspace, plan, subscription = await build_billing_summary(session, workspace_id)
    usage = await build_usage_summary(session, workspace_id)
    return BillingSummaryResponse(
        workspace_id=workspace.id,
        plan=plan,
        subscription=(
            BillingSubscriptionResponse(
                workspace_id=subscription.workspace_id,
                plan_slug=plan.slug if plan else None,
                status=subscription.status,
                stripe_customer_id=subscription.stripe_customer_id,
                stripe_subscription_id=subscription.stripe_subscription_id,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end,
            )
            if subscription is not None
            else None
        ),
        usage=UsageSummaryResponse(
            plan_slug=usage.plan_slug,
            period_start=usage.period_start,
            period_end=usage.period_end,
            items=[
                UsageItemResponse(metric=item.metric, used=item.used, limit=item.limit)
                for item in usage.items
            ],
        ),
    )


@router.post(
    "/workspaces/{workspace_id}/checkout",
    response_model=BillingSessionResponse,
)
async def create_billing_checkout(
    workspace_id: UUID,
    payload: BillingCheckoutRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BillingSessionResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    try:
        url, session_id = await create_checkout_session(session, workspace_id, payload)
    except BillingConfigError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "billing_unavailable", "message": str(exc)},
        ) from exc
    return BillingSessionResponse(url=url, provider_session_id=session_id)


@router.post(
    "/workspaces/{workspace_id}/portal",
    response_model=BillingSessionResponse,
)
async def create_billing_portal(
    workspace_id: UUID,
    payload: BillingPortalRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BillingSessionResponse:
    await _require_workspace_access(session, current_user, workspace_id)
    try:
        url, session_id = await create_portal_session(session, workspace_id, payload)
    except BillingConfigError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "billing_unavailable", "message": str(exc)},
        ) from exc
    return BillingSessionResponse(url=url, provider_session_id=session_id)


@router.post("/webhook")
async def billing_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    stripe_signature: Annotated[str | None, Header(alias="Stripe-Signature")] = None,
) -> dict[str, str]:
    if not stripe_signature:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "billing_webhook_missing_signature",
                "message": "Missing Stripe-Signature header.",
            },
        )
    body = await request.body()
    try:
        return await handle_stripe_event(session, body, stripe_signature)
    except (BillingConfigError, BillingWebhookError) as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "billing_webhook_error", "message": str(exc)},
        ) from exc


async def _require_workspace_access(
    session: AsyncSession,
    current_user: CurrentUser,
    workspace_id: UUID,
) -> None:
    try:
        await require_workspace_role(
            session,
            current_user.user,
            workspace_id,
            {WorkspaceRole.OWNER, WorkspaceRole.ADMIN},
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "workspace_forbidden",
                "message": "Workspace access is required.",
            },
        ) from exc
