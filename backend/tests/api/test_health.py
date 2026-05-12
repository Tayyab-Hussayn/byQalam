import httpx
import pytest

from app.api.v1 import health as health_module
from app.db.session import get_db_session
from app.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint_returns_service_status() -> None:
    transport = httpx.ASGITransport(app=create_app())

    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Qalam API"
    assert body["environment"] in {"local", "test", "staging", "production"}
    assert "checked_at" in body
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_ready_endpoint_returns_readiness_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_check_database(_session: object) -> dict[str, str]:
        return {
            "database_name": "qalam",
            "database_user": "postgres",
            "database_version": "PostgreSQL test",
        }

    async def fake_db_session() -> object:
        yield object()

    monkeypatch.setattr(health_module, "check_database", fake_check_database)
    app = create_app()
    app.dependency_overrides[get_db_session] = fake_db_session
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"]["database_name"] == "qalam"
