from fastapi import HTTPException

import app.core.api_errors as api_errors
from app.core.api_errors import build_error_payload, http_exception_handler


async def test_http_exception_handler_normalizes_detail_and_request_id(monkeypatch):
    token = api_errors.request_id_context.set("req-123")

    try:
        response = await http_exception_handler(
            None,  # type: ignore[arg-type]
            HTTPException(
                status_code=404,
                detail={"code": "not_found", "message": "Missing"},
            ),
        )

        assert response.status_code == 404
        assert response.body.decode().find('"code":"not_found"') != -1
        assert response.body.decode().find('"request_id":"req-123"') != -1
    finally:
        api_errors.request_id_context.reset(token)


def test_build_error_payload_includes_details() -> None:
    payload = build_error_payload(
        "rate_limited",
        "Too many requests.",
        {"limit": 10},
    )

    assert payload["detail"]["code"] == "rate_limited"
    assert payload["detail"]["message"] == "Too many requests."
    assert payload["detail"]["details"]["limit"] == 10
