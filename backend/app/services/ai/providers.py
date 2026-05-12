from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GenerationContext:
    prompt: str
    niche_slug: str | None
    target_audience: str | None
    tone: str | None
    language: str
    content_goals: list[str]
    topics_to_avoid: list[str]
    voice_traits: list[str]
    writing_sample_snippets: list[str]


@dataclass(frozen=True)
class GeneratedPost:
    body: str
    hashtags: list[str]
    first_comment: str | None
    quality_score: int
    tokens_input: int
    tokens_output: int
    estimated_cost_cents: int


class ContentGenerationProvider(Protocol):
    provider_name: str
    model_name: str

    async def generate_post(self, context: GenerationContext) -> GeneratedPost:
        raise NotImplementedError
