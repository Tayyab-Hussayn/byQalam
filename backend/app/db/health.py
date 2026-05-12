from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_database(session: AsyncSession) -> dict[str, str]:
    result = await session.execute(
        text(
            """
            select
              current_database() as database_name,
              current_user as database_user,
              version() as database_version
            """
        )
    )
    row = result.mappings().one()
    return {
        "database_name": row["database_name"],
        "database_user": row["database_user"],
        "database_version": row["database_version"],
    }
