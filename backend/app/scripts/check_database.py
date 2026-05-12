import asyncio
import socket
from urllib.parse import urlparse

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.health import check_database
from app.db.session import AsyncSessionLocal


async def main() -> None:
    has_password_placeholder = (
        "[YOUR-PASSWORD]" in settings.database_url
        or "PASSWORD" in settings.database_url
    )
    if has_password_placeholder:
        print(
            "Database connection failed: "
            "DATABASE_URL still contains a password placeholder."
        )
        print("Replace [YOUR-PASSWORD] with the real Supabase database password.")
        raise SystemExit(1)

    if not _can_open_tcp_connection(settings.database_url):
        raise SystemExit(1)

    try:
        database = await asyncio.wait_for(
            _check_database(),
            timeout=settings.database_connect_timeout_seconds,
        )
    except TimeoutError as exc:
        print(
            "Database connection failed: "
            f"timed out after {settings.database_connect_timeout_seconds} seconds."
        )
        raise SystemExit(1) from exc
    except SQLAlchemyError as exc:
        print(f"Database connection failed: {exc}")
        raise SystemExit(1) from exc

    print("Database connection OK")
    print(f"Database: {database['database_name']}")
    print(f"User: {database['database_user']}")
    print(f"Version: {database['database_version']}")


async def _check_database() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        return await check_database(session)


def _can_open_tcp_connection(database_url: str) -> bool:
    parsed = urlparse(database_url.replace("postgresql+asyncpg://", "postgresql://"))
    host = parsed.hostname
    port = parsed.port or 5432

    if not host:
        print("Database connection failed: DATABASE_URL has no hostname.")
        return False

    if not host.endswith("supabase.com") and "localhost" not in host:
        print(f"Database connection failed: parsed hostname is '{host}'.")
        print(
            "If this is a Supabase URL, your password likely contains special "
            "characters that must be URL-encoded."
        )
        print("Example: @ becomes %40, # becomes %23, / becomes %2F, : becomes %3A")
        return False

    try:
        with socket.create_connection(
            (host, port),
            timeout=settings.database_connect_timeout_seconds,
        ):
            return True
    except OSError as exc:
        print(f"Database TCP connection failed for {host}:{port}: {exc}")
        return False


if __name__ == "__main__":
    asyncio.run(main())
