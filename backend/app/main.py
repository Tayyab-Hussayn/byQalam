from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.api_errors import (
    build_error_payload,
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.core.sentry import configure_sentry
from app.services.usage import QuotaExceededError


def create_app() -> FastAPI:
    configure_sentry()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        openapi_url=f"{settings.app_api_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(QuotaExceededError, quota_exceeded_handler)
    app.add_exception_handler(Exception, internal_exception_handler)

    app.include_router(api_router, prefix=settings.app_api_prefix)
    return app


async def quota_exceeded_handler(
    _request: Request,
    exc: QuotaExceededError,
) -> JSONResponse:
    return JSONResponse(
        status_code=402,
        content=build_error_payload(
            "quota_exceeded",
            str(exc),
            {
                "metric": exc.metric.value,
                "limit": exc.limit,
            },
        ),
    )


app = create_app()
