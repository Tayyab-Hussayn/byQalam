from collections.abc import Callable
from time import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.api_errors import build_error_payload
from app.core.config import settings
from app.core.redis import get_redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Any],
    ) -> JSONResponse:
        if not settings.enable_rate_limiting or not request.url.path.startswith(
            settings.app_api_prefix
        ):
            return await call_next(request)

        if request.url.path in {
            f"{settings.app_api_prefix}/health",
            f"{settings.app_api_prefix}/ready",
            f"{settings.app_api_prefix}/openapi.json",
        }:
            return await call_next(request)

        limit = settings.rate_limit_requests_per_minute
        bucket = int(time() // 60)
        client_ip = _get_client_ip(request)
        key = f"qalam:rate:{client_ip}:{request.method}:{request.url.path}:{bucket}"
        redis = get_redis_client()

        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, 60)
            ttl = await redis.ttl(key)
            remaining = max(limit - count, 0)
            if count > limit:
                return JSONResponse(
                    status_code=429,
                    content=build_error_payload(
                        "rate_limited",
                        "Too many requests.",
                        {
                            "limit": limit,
                            "retry_after_seconds": max(ttl, 1),
                        },
                    ),
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(max(ttl, 1)),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            if ttl > 0:
                response.headers["X-RateLimit-Reset"] = str(ttl)
            return response
        except Exception:
            return await call_next(request)


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"
