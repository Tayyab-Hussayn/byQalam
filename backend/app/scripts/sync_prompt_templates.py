import asyncio

from app.db.session import AsyncSessionLocal
from app.services.prompt_seed import sync_prompt_templates


async def main() -> None:
    async with AsyncSessionLocal() as session:
        templates = await sync_prompt_templates(session)
    print(f"Synced prompt templates: {len(templates)}")


if __name__ == "__main__":
    asyncio.run(main())
