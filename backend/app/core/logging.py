import logging
from contextvars import ContextVar
from uuid import uuid4

import structlog

from app.core.config import settings

request_id_context: ContextVar[str] = ContextVar("request_id", default="")


def configure_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_request_id,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )


def generate_request_id() -> str:
    return uuid4().hex


def add_request_id(
    _logger: object,
    _method_name: str,
    event_dict: dict[str, object],
) -> dict[str, object]:
    request_id = request_id_context.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict
