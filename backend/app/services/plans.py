from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.models.plan import Plan
from app.schemas.plan import PlanQuota, PlanSeed


def build_plan_seeds(settings: Settings) -> list[PlanSeed]:
    return [
        PlanSeed(
            slug="free",
            name="Free",
            sort_order=10,
            quotas=PlanQuota(
                monthly_ai_generations=settings.free_monthly_ai_generations,
                monthly_scheduled_posts=settings.free_monthly_scheduled_posts,
                max_workspaces=settings.free_max_workspaces,
                max_members=settings.free_max_members,
                max_linkedin_connections=settings.free_max_linkedin_connections,
                media_storage_mb=settings.free_media_storage_mb,
            ),
        ),
        PlanSeed(
            slug="starter",
            name="Starter",
            sort_order=20,
            stripe_price_id=settings.stripe_price_starter,
            quotas=PlanQuota(
                monthly_ai_generations=settings.starter_monthly_ai_generations,
                monthly_scheduled_posts=settings.starter_monthly_scheduled_posts,
                max_workspaces=settings.starter_max_workspaces,
                max_members=settings.starter_max_members,
                max_linkedin_connections=settings.starter_max_linkedin_connections,
                media_storage_mb=settings.starter_media_storage_mb,
            ),
        ),
        PlanSeed(
            slug="pro",
            name="Pro",
            sort_order=30,
            stripe_price_id=settings.stripe_price_pro,
            quotas=PlanQuota(
                monthly_ai_generations=settings.pro_monthly_ai_generations,
                monthly_scheduled_posts=settings.pro_monthly_scheduled_posts,
                max_workspaces=settings.pro_max_workspaces,
                max_members=settings.pro_max_members,
                max_linkedin_connections=settings.pro_max_linkedin_connections,
                media_storage_mb=settings.pro_media_storage_mb,
            ),
        ),
        PlanSeed(
            slug="agency",
            name="Agency",
            sort_order=40,
            stripe_price_id=settings.stripe_price_agency,
            quotas=PlanQuota(
                monthly_ai_generations=settings.agency_monthly_ai_generations,
                monthly_scheduled_posts=settings.agency_monthly_scheduled_posts,
                max_workspaces=settings.agency_max_workspaces,
                max_members=settings.agency_max_members,
                max_linkedin_connections=settings.agency_max_linkedin_connections,
                media_storage_mb=settings.agency_media_storage_mb,
            ),
        ),
    ]


async def sync_plan_limits(session: AsyncSession, settings: Settings) -> list[Plan]:
    synced: list[Plan] = []

    for seed in build_plan_seeds(settings):
        existing = await session.scalar(select(Plan).where(Plan.slug == seed.slug))
        quotas = seed.quotas.model_dump()

        if existing is None:
            plan = Plan(
                slug=seed.slug,
                name=seed.name,
                stripe_price_id=seed.stripe_price_id,
                quotas=quotas,
                sort_order=seed.sort_order,
            )
            session.add(plan)
            synced.append(plan)
            continue

        existing.name = seed.name
        existing.stripe_price_id = seed.stripe_price_id
        existing.quotas = quotas
        existing.sort_order = seed.sort_order
        existing.is_active = True
        synced.append(existing)

    await session.commit()
    return synced
