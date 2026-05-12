from datetime import datetime
from uuid import uuid4

from app.db.models.enums import PostStatus
from app.db.models.post import Post
from app.schemas.post import PostRejectRequest, PostScheduleRequest
from app.services.posts import delete_post, reject_post, schedule_post


async def test_reject_post_sets_status_and_reason() -> None:
    post = Post(
        workspace_id=uuid4(),
        author_user_id=uuid4(),
        body="Draft",
        hashtags=[],
    )

    class FakeSession:
        def add(self, _value: object) -> None:
            return None

        async def commit(self) -> None:
            return None

        async def refresh(self, _post: Post) -> None:
            return None

    updated = await reject_post(
        FakeSession(),
        post,
        PostRejectRequest(reason="Not aligned"),
    )

    assert updated.status == PostStatus.REJECTED
    assert updated.rejection_reason == "Not aligned"


async def test_schedule_post_sets_schedule_fields(monkeypatch) -> None:
    post = Post(
        workspace_id=uuid4(),
        author_user_id=uuid4(),
        body="Approved",
        hashtags=[],
        status=PostStatus.APPROVED,
    )

    class FakeSession:
        async def scalar(self, *_args: object) -> None:
            return None

        def add(self, _value: object) -> None:
            return None

        async def commit(self) -> None:
            return None

        async def refresh(self, _post: Post) -> None:
            return None

    async def fake_assert_quota_available(*_args: object) -> None:
        return None

    async def fake_record_usage(*_args: object) -> None:
        return None

    monkeypatch.setattr(
        "app.services.posts.assert_quota_available",
        fake_assert_quota_available,
    )
    monkeypatch.setattr("app.services.posts.record_usage", fake_record_usage)

    scheduled_for = datetime(2026, 5, 11, 9, 30)
    updated = await schedule_post(
        FakeSession(),
        post,
        PostScheduleRequest(scheduled_for=scheduled_for, timezone="Asia/Karachi"),
    )

    assert updated.status == PostStatus.SCHEDULED
    assert updated.scheduled_for == scheduled_for
    assert updated.timezone == "Asia/Karachi"


async def test_delete_post_removes_draft_post(monkeypatch) -> None:
    post = Post(
        workspace_id=uuid4(),
        author_user_id=uuid4(),
        body="Draft",
        hashtags=[],
        status=PostStatus.DRAFT,
    )

    class FakeSession:
        def __init__(self) -> None:
            self.deleted = None
            self.committed = False

        async def delete(self, value: Post) -> None:
            self.deleted = value

        async def commit(self) -> None:
            self.committed = True

    async def fake_record_audit_event(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(
        "app.services.posts.record_audit_event",
        fake_record_audit_event,
    )

    session = FakeSession()
    await delete_post(session, post)

    assert session.deleted is post
    assert session.committed is True
