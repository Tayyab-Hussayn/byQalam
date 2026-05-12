from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContentPreferenceBase(BaseModel):
    niche_slug: str | None = Field(default=None, max_length=120)
    target_audience: str | None = Field(default=None, max_length=500)
    content_goals: list[str] = Field(default_factory=list)
    tone: str | None = Field(default=None, max_length=120)
    language: str = Field(default="en", min_length=2, max_length=20)
    post_style: str | None = Field(default=None, max_length=120)
    cta_preference: str | None = Field(default=None, max_length=120)
    hashtag_policy: str | None = Field(default=None, max_length=120)
    emoji_policy: str | None = Field(default=None, max_length=120)
    topics_to_avoid: list[str] = Field(default_factory=list)
    preferred_post_length: str | None = Field(default=None, max_length=80)


class ContentPreferenceUpsertRequest(ContentPreferenceBase):
    pass


class ContentPreferenceResponse(ContentPreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID


class VoiceProfileBase(BaseModel):
    summary: str | None = None
    traits: list[str] = Field(default_factory=list)
    banned_phrases: list[str] = Field(default_factory=list)
    confidence_score: int = Field(default=0, ge=0, le=100)


class VoiceProfileUpsertRequest(VoiceProfileBase):
    pass


class VoiceProfileResponse(VoiceProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    sample_count: int


class WritingSampleCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=20)
    source: str | None = Field(default=None, max_length=120)


class WritingSampleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    title: str | None = None
    body: str
    source: str | None = None


class WritingSampleListResponse(BaseModel):
    samples: list[WritingSampleResponse]


class NicheProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    description: str | None = None
    audience_types: list[str]
    content_pillars: list[str]
    hook_patterns: list[str]
    cta_examples: list[str]
    risky_claims_to_avoid: list[str]
    hashtag_guidance: list[str]


class NicheProfileListResponse(BaseModel):
    niches: list[NicheProfileResponse]
