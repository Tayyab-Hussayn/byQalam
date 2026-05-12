from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_supabase_jwt
from app.db.models.user import User
from app.db.session import get_db_session
from app.services.users import sync_authenticated_user

bearer_scheme = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class CurrentUser:
    user: User


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CurrentUser:
    claims = decode_supabase_jwt(credentials.credentials)
    user = await sync_authenticated_user(session, claims)
    return CurrentUser(user=user)
