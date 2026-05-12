from uuid import uuid4

from app.services.notifications import create_failure_notification


async def test_create_failure_notification_adds_notification_to_session() -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.added = []

        def add(self, value: object) -> None:
            self.added.append(value)

    workspace_id = uuid4()
    session = FakeSession()

    notification = await create_failure_notification(
        session,
        workspace_id=workspace_id,
        title="Generation failed",
        body="The model request failed.",
        entity_type="ai_generation_run",
        entity_id="run-123",
        metadata={"provider": "mock"},
    )

    assert notification in session.added
    assert notification.workspace_id == workspace_id
    assert notification.title == "Generation failed"
    assert notification.entity_type == "ai_generation_run"
    assert notification.metadata_json == {"provider": "mock"}
