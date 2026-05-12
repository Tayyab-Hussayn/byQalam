from collections.abc import Mapping
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import request_id_context


def build_error_payload(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if details:
        payload["details"] = details
    request_id = request_id_context.get()
    if request_id:
        payload["request_id"] = request_id
    return {"detail": payload}


def _detail_from_http_exception(detail: Any) -> tuple[str, str, dict[str, Any] | None]:
    if isinstance(detail, Mapping):
        code = str(detail.get("code", "http_error"))
        message = str(detail.get("message", "Request failed"))
        extra = {
            key: value
            for key, value in detail.items()
            if key not in {"code", "message"}
        }
        return code, message, extra or None
    if isinstance(detail, str):
        return "http_error", detail, None
    return "http_error", "Request failed", {"detail": detail}


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    code, message, details = _detail_from_http_exception(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_payload(code, message, details),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=build_error_payload(
            "validation_error",
            "Request validation failed.",
            {"errors": exc.errors()},
        ),
    )


async def internal_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=build_error_payload(
            "internal_error",
            "An unexpected error occurred.",
        ),
    )
