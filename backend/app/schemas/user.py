from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_auth_id: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
