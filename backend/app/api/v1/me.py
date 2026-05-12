from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.me import MeResponse
from app.schemas.user import UserResponse
from app.schemas.workspace import WorkspaceResponse
from app.services.workspaces import list_user_workspaces

router = APIRouter(prefix="/me")


@router.get("", response_model=MeResponse)
async def get_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MeResponse:
    memberships = await list_user_workspaces(session, current_user.user)
    return MeResponse(
        user=UserResponse.model_validate(current_user.user),
        workspaces=[
            WorkspaceResponse.model_validate(workspace).model_copy(
                update={"role": role}
            )
            for workspace, role in memberships
        ],
    )
