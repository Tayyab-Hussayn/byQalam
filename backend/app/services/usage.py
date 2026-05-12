from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import (
    LinkedinConnectionStatus,
    SubscriptionStatus,
    UsageMetric,
)
from app.db.models.plan import Plan
from app.db.models.subscription import Subscription
from app.db.models.usage import UsageLedger
from app.db.models.workspace import Workspace, WorkspaceMember


class QuotaExceededError(RuntimeError):
    def __init__(self, metric: UsageMetric, limit: int) -> None:
        super().__init__(f"Quota exceeded for {metric.value}")
        self.metric = metric
        self.limit = limit


@dataclass(frozen=True)
class UsageItem:
    metric: UsageMetric
    used: int
    limit: int | None


@dataclass(frozen=True)
class UsageSummary:
    plan_slug: str
    period_start: datetime
    period_end: datetime
    items: list[UsageItem]


QUOTA_BY_METRIC = {
    UsageMetric.AI_GENERATION: "monthly_ai_generations",
    UsageMetric.AI_REGENERATION: "monthly_ai_generations",
    UsageMetric.SCHEDULED_POST: "monthly_scheduled_posts",
    UsageMetric.PUBLISHED_POST: "monthly_scheduled_posts",
    UsageMetric.CONNECTED_LINKEDIN_ACCOUNT: "max_linkedin_connections",
    UsageMetric.MEDIA_STORAGE_MB: "media_storage_mb",
}


def current_month_period(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now or datetime.utcnow()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


async def get_workspace_plan(session: AsyncSession, workspace_id: UUID) -> Plan:
    active_statuses = {SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING}
    subscription = await session.scalar(
        select(Subscription)
        .where(
            Subscription.workspace_id == workspace_id,
            Subscription.status.in_(active_statuses),
        )
        .order_by(Subscription.created_at.desc())
    )
    if subscription is not None:
        plan = await session.get(Plan, subscription.plan_id)
        if plan is not None and plan.is_active:
            return plan

    plan = await session.scalar(select(Plan).where(Plan.slug == "free"))
    if plan is None:
        raise RuntimeError("Free plan is not configured")
    return plan


async def get_user_plan(session: AsyncSession, user_id: UUID) -> Plan:
    plans = await session.scalars(
        select(Plan)
        .join(Subscription, Subscription.plan_id == Plan.id)
        .join(Workspace, Workspace.id == Subscription.workspace_id)
        .join(
            WorkspaceMember,
            WorkspaceMember.workspace_id == Workspace.id,
        )
        .where(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.is_active.is_(True),
            Subscription.status.in_(
                {SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING}
            ),
            Plan.is_active.is_(True),
        )
        .order_by(Plan.sort_order.desc())
    )
    best = plans.first()
    if best is not None:
        return best
    plan = await session.scalar(select(Plan).where(Plan.slug == "free"))
    if plan is None:
        raise RuntimeError("Free plan is not configured")
    return plan


async def get_usage_amount(
    session: AsyncSession,
    workspace_id: UUID,
    metric: UsageMetric,
    period_start: datetime,
    period_end: datetime,
) -> int:
    amount = await session.scalar(
        select(func.coalesce(func.sum(UsageLedger.amount), 0)).where(
            UsageLedger.workspace_id == workspace_id,
            UsageLedger.metric == metric,
            UsageLedger.period_start >= period_start,
            UsageLedger.period_start < period_end,
        )
    )
    return int(amount or 0)


async def assert_quota_available(
    session: AsyncSession,
    workspace_id: UUID,
    metric: UsageMetric,
    amount: int = 1,
) -> None:
    plan = await get_workspace_plan(session, workspace_id)
    quota_key = QUOTA_BY_METRIC.get(metric)
    if quota_key is None:
        return
    limit = plan.quotas.get(quota_key)
    if limit is None or limit < 0:
        return

    period_start, period_end = current_month_period()
    used = await get_usage_amount(
        session,
        workspace_id,
        metric,
        period_start,
        period_end,
    )
    if used + amount > limit:
        raise QuotaExceededError(metric, limit)


async def count_active_workspace_members(
    session: AsyncSession,
    workspace_id: UUID,
) -> int:
    amount = await session.scalar(
        select(func.count(WorkspaceMember.id)).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.is_active.is_(True),
        )
    )
    return int(amount or 0)


async def assert_member_capacity(
    session: AsyncSession,
    workspace_id: UUID,
    amount: int = 1,
) -> None:
    plan = await get_workspace_plan(session, workspace_id)
    limit = plan.quotas.get("max_members")
    if limit is None or limit < 0:
        return
    used = await count_active_workspace_members(session, workspace_id)
    if used + amount > limit:
        raise QuotaExceededError(UsageMetric.MEMBER_COUNT, limit)


async def count_active_linkedin_connections(
    session: AsyncSession,
    workspace_id: UUID,
) -> int:
    from app.db.models.linkedin import LinkedinConnection

    amount = await session.scalar(
        select(func.count(LinkedinConnection.id)).where(
            LinkedinConnection.workspace_id == workspace_id,
            LinkedinConnection.status == LinkedinConnectionStatus.CONNECTED,
        )
    )
    return int(amount or 0)


async def assert_linkedin_connection_capacity(
    session: AsyncSession,
    workspace_id: UUID,
    amount: int = 1,
) -> None:
    plan = await get_workspace_plan(session, workspace_id)
    limit = plan.quotas.get("max_linkedin_connections")
    if limit is None or limit < 0:
        return
    used = await count_active_linkedin_connections(session, workspace_id)
    if used + amount > limit:
        raise QuotaExceededError(UsageMetric.CONNECTED_LINKEDIN_ACCOUNT, limit)


async def assert_workspace_capacity(
    session: AsyncSession,
    user_id: UUID,
    amount: int = 1,
) -> None:
    plan = await get_user_plan(session, user_id)
    limit = plan.quotas.get("max_workspaces")
    if limit is None or limit < 0:
        return
    used = await session.scalar(
        select(func.count(Workspace.id))
        .join(
            WorkspaceMember,
            WorkspaceMember.workspace_id == Workspace.id,
        )
        .where(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.is_active.is_(True),
            Workspace.is_active.is_(True),
        )
    )
    if int(used or 0) + amount > limit:
        raise QuotaExceededError(UsageMetric.WORKSPACE_COUNT, limit)


async def record_usage(
    session: AsyncSession,
    workspace_id: UUID,
    metric: UsageMetric,
    amount: int = 1,
    metadata: dict | None = None,
) -> None:
    period_start, period_end = current_month_period()
    session.add(
        UsageLedger(
            workspace_id=workspace_id,
            metric=metric,
            amount=amount,
            period_start=period_start,
            period_end=period_end,
            metadata_json=metadata or {},
        )
    )


async def build_usage_summary(
    session: AsyncSession,
    workspace_id: UUID,
) -> UsageSummary:
    plan = await get_workspace_plan(session, workspace_id)
    period_start, period_end = current_month_period()
    items = []
    for metric, quota_key in QUOTA_BY_METRIC.items():
        used = await get_usage_amount(
            session,
            workspace_id,
            metric,
            period_start,
            period_end,
        )
        items.append(
            UsageItem(
                metric=metric,
                used=used,
                limit=plan.quotas.get(quota_key),
            )
        )
    return UsageSummary(
        plan_slug=plan.slug,
        period_start=period_start,
        period_end=period_end,
        items=items,
    )
