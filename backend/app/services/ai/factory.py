from app.core.config import settings
from app.services.ai.http_providers import (
    AnthropicProvider,
    GoogleProvider,
    GroqProvider,
    MistralProvider,
    OpenAIProvider,
    OpenCodeProvider,
)
from app.services.ai.mock_provider import MockContentGenerationProvider
from app.services.ai.providers import ContentGenerationProvider


def get_generation_provider() -> ContentGenerationProvider:
    if settings.ai_default_provider == "mock":
        return MockContentGenerationProvider()
    if settings.ai_default_provider == "openai":
        return OpenAIProvider("openai")
    if settings.ai_default_provider == "anthropic":
        return AnthropicProvider("anthropic")
    if settings.ai_default_provider == "google":
        return GoogleProvider("google")
    if settings.ai_default_provider == "groq":
        return GroqProvider("groq")
    if settings.ai_default_provider == "mistral":
        return MistralProvider("mistral")
    if settings.ai_default_provider == "opencode":
        return OpenCodeProvider("opencode")

    raise NotImplementedError(
        f"AI provider '{settings.ai_default_provider}' is not implemented yet."
    )
