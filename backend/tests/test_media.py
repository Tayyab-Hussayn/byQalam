from uuid import uuid4

from app.db.models.post import Post
from app.schemas.media import PostMediaCreateRequest
from app.services.media import attach_post_media


async def test_attach_post_media_records_usage(monkeypatch) -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.added = []
            self.committed = False

        def add(self, value: object) -> None:
            self.added.append(value)

        async def commit(self) -> None:
            self.committed = True

        async def refresh(self, _value: object) -> None:
            return None

    calls = []

    async def fake_assert_quota_available(*args: object, **kwargs: object) -> None:
        calls.append(("assert", args, kwargs))

    async def fake_record_usage(*args: object, **kwargs: object) -> None:
        calls.append(("usage", args, kwargs))

    monkeypatch.setattr(
        "app.services.media.assert_quota_available",
        fake_assert_quota_available,
    )
    monkeypatch.setattr("app.services.media.record_usage", fake_record_usage)

    post = Post(
        workspace_id=uuid4(),
        author_user_id=uuid4(),
        body="Draft",
        hashtags=[],
    )
    session = FakeSession()

    media = await attach_post_media(
        session,
        post,
        PostMediaCreateRequest(
            storage_path="media/post-1/image.png",
            media_type="image/png",
            original_filename="image.png",
            size_bytes=2 * 1024 * 1024,
        ),
    )

    assert session.committed is True
    assert media.storage_path == "media/post-1/image.png"
    assert calls[0][0] == "assert"
    assert calls[0][2]["amount"] == 2
    assert calls[1][0] == "usage"
    assert calls[1][2]["amount"] == 2
    assert calls[1][2]["metadata"]["media_type"] == "image/png"
