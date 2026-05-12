from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthClaims
from app.db.models.user import User


async def sync_authenticated_user(
    session: AsyncSession,
    claims: AuthClaims,
) -> User:
    user = await session.scalar(
        select(User).where(User.external_auth_id == claims.external_auth_id)
    )

    if user is None:
        user = User(
            external_auth_id=claims.external_auth_id,
            email=claims.email,
            full_name=claims.full_name,
            avatar_url=claims.avatar_url,
        )
        session.add(user)
    else:
        user.email = claims.email
        user.full_name = claims.full_name
        user.avatar_url = claims.avatar_url
        user.is_active = True

    await session.commit()
    await session.refresh(user)
    return user
