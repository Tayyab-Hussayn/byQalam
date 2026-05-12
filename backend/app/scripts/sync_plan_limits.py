import asyncio

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.plans import sync_plan_limits


async def main() -> None:
    async with AsyncSessionLocal() as session:
        plans = await sync_plan_limits(session, settings)
    slugs = ", ".join(plan.slug for plan in plans)
    print(f"Synced plan limits: {slugs}")


if __name__ == "__main__":
    asyncio.run(main())
