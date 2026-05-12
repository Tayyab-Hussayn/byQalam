import asyncio
from datetime import datetime

from app.db.session import async_session_factory
from app.services.publishing import publish_due_scheduled_posts


async def _main(limit: int) -> None:
    async with async_session_factory() as session:
        result = await publish_due_scheduled_posts(
            session,
            due_at=datetime.utcnow(),
            limit=limit,
        )
    print(
        {
            "scanned": result.scanned,
            "published": result.published,
            "failed": result.failed,
        }
    )


def main() -> None:
    asyncio.run(_main(limit=25))


if __name__ == "__main__":
    main()
