from starlette.requests import Request
from starlette.responses import Response

from app.core.rate_limit import RateLimitMiddleware


class FakeRedis:
    def __init__(self) -> None:
        self.count = 0

    async def incr(self, _key: str) -> int:
        self.count += 1
        return self.count

    async def expire(self, _key: str, _seconds: int) -> None:
        return None

    async def ttl(self, _key: str) -> int:
        return 60


async def test_rate_limit_middleware_blocks_over_limit(monkeypatch) -> None:
    from app.core.config import settings

    original_limit = settings.rate_limit_requests_per_minute
    settings.rate_limit_requests_per_minute = 1

    fake_redis = FakeRedis()
    monkeypatch.setattr(
        "app.core.rate_limit.get_redis_client",
        lambda: fake_redis,
    )

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/workspaces",
        "raw_path": b"/api/v1/workspaces",
        "query_string": b"",
        "headers": [(b"host", b"testserver")],
        "client": ("127.0.0.1", 1234),
        "scheme": "http",
        "server": ("testserver", 80),
    }
    request = Request(scope, receive)
    middleware = RateLimitMiddleware(app=None)  # type: ignore[arg-type]

    async def call_next(_request: Request) -> Response:
        return Response("ok")

    first = await middleware.dispatch(request, call_next)
    second = await middleware.dispatch(request, call_next)

    settings.rate_limit_requests_per_minute = original_limit

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["X-RateLimit-Limit"] == "1"
