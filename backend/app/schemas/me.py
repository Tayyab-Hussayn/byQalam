from pydantic import BaseModel

from app.schemas.user import UserResponse
from app.schemas.workspace import WorkspaceResponse


class MeResponse(BaseModel):
    user: UserResponse
    workspaces: list[WorkspaceResponse]
