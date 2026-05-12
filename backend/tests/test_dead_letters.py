from uuid import uuid4

from app.services.dead_letters import record_dead_letter


async def test_record_dead_letter_adds_job_to_session() -> None:
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

    session = FakeSession()
    workspace_id = uuid4()
    job = await record_dead_letter(
        session,
        task_name="qalam.generate_post_for_workspace",
        task_id="task-123",
        workspace_id=workspace_id,
        entity_type="workspace",
        entity_id=str(workspace_id),
        payload={"prompt": "Hello"},
        error={"type": "RuntimeError", "error": "boom"},
        retries=3,
        max_retries=3,
    )

    assert job in session.added
    assert session.committed is True
    assert job.task_name == "qalam.generate_post_for_workspace"
    assert job.entity_type == "workspace"
    assert job.error_json["error"] == "boom"
