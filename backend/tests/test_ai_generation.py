from uuid import uuid4

from app.db.models.notification import Notification
from app.db.models.user import User
from app.schemas.generation import GeneratePostRequest
from app.services.ai.mock_provider import MockContentGenerationProvider
from app.services.ai.providers import GenerationContext
from app.services.generation import generate_post_for_workspace


async def test_mock_provider_generates_contextual_linkedin_post() -> None:
    provider = MockContentGenerationProvider()

    generated = await provider.generate_post(
        GenerationContext(
            prompt="Hiring senior backend engineers",
            niche_slug="hr_recruiting",
            target_audience="technical hiring managers",
            tone="practical",
            language="en",
            content_goals=["build trust"],
            topics_to_avoid=["salary claims"],
            voice_traits=["clear", "direct"],
            writing_sample_snippets=["We share specific hiring lessons."],
        )
    )

    assert "Hiring senior backend engineers" in generated.body
    assert "technical hiring managers" in generated.body
    assert "#linkedin" in generated.hashtags
    assert generated.quality_score > 0


async def test_generation_failure_creates_notification(monkeypatch) -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.added = []
            self.committed = False

        def add(self, value: object) -> None:
            self.added.append(value)

        async def flush(self) -> None:
            return None

        async def commit(self) -> None:
            self.committed = True

    class FakeProvider:
        provider_name = "mock"
        model_name = "mock-model"

        async def generate_post(self, _context: GenerationContext):
            raise RuntimeError("provider exploded")

    async def fake_assert_quota_available(*_args: object, **_kwargs: object) -> None:
        return None

    async def fake_build_generation_context(
        *_args: object,
        **_kwargs: object,
    ) -> GenerationContext:
        return GenerationContext(
            prompt="Launch post",
            niche_slug="founders",
            target_audience="startup founders",
            tone="confident",
            language="en",
            content_goals=[],
            topics_to_avoid=[],
            voice_traits=[],
            writing_sample_snippets=[],
        )

    async def fake_get_active_prompt_template(
        *_args: object,
        **_kwargs: object,
    ) -> None:
        return None

    async def fake_record_usage(*_args: object, **_kwargs: object) -> None:
        return None

    async def fake_record_audit_event(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(
        "app.services.generation.assert_quota_available",
        fake_assert_quota_available,
    )
    monkeypatch.setattr(
        "app.services.generation.build_generation_context",
        fake_build_generation_context,
    )
    monkeypatch.setattr(
        "app.services.generation.get_generation_provider",
        lambda: FakeProvider(),
    )
    monkeypatch.setattr(
        "app.services.generation.get_active_prompt_template",
        fake_get_active_prompt_template,
    )
    monkeypatch.setattr("app.services.generation.record_usage", fake_record_usage)
    monkeypatch.setattr(
        "app.services.generation.record_audit_event",
        fake_record_audit_event,
    )

    session = FakeSession()
    user = User(
        id=uuid4(),
        external_auth_id="auth-user-1",
        email="user@example.com",
        full_name="Test User",
        avatar_url=None,
        is_active=True,
    )

    try:
        await generate_post_for_workspace(
            session,
            uuid4(),
            user,
            GeneratePostRequest(prompt="Launch post"),
        )
    except RuntimeError as exc:
        assert "provider exploded" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("generation should have failed")

    notifications = [item for item in session.added if isinstance(item, Notification)]
    assert notifications
    assert notifications[0].title == "AI generation failed"
    assert session.committed is True
