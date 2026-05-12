import asyncio

from app.db.session import AsyncSessionLocal
from app.services.niche_seed import sync_niche_profiles


async def main() -> None:
    async with AsyncSessionLocal() as session:
        niches = await sync_niche_profiles(session)
    print(f"Synced niche profiles: {len(niches)}")


if __name__ == "__main__":
    asyncio.run(main())
