from app.core.config import settings
from app.services.ai.http_providers import OpenCodeProvider
from app.services.ai.mock_provider import MockContentGenerationProvider
from app.services.ai.providers import ContentGenerationProvider


def get_generation_provider() -> ContentGenerationProvider:
    if settings.ai_default_provider == "mock":
        return MockContentGenerationProvider()
    if settings.ai_default_provider == "opencode":
        return OpenCodeProvider("opencode")

    raise NotImplementedError(
        f"AI provider '{settings.ai_default_provider}' is not implemented yet."
    )