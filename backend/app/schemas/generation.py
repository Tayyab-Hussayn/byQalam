from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.post import PostResponse


class GeneratePostRequest(BaseModel):
    prompt: str = Field(min_length=3)
    tone: str | None = Field(default=None, max_length=120)
    niche_slug: str | None = Field(default=None, max_length=120)
    title_internal: str | None = Field(default=None, max_length=255)


class RegeneratePostRequest(BaseModel):
    reason: str = Field(default="custom_instruction", max_length=255)
    instruction: str | None = Field(default=None, max_length=1000)


class GeneratePostResponse(BaseModel):
    post: PostResponse
    generation_run_id: UUID
    quality_score: int | None = None
