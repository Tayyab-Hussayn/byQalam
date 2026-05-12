from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    checked_at: datetime


class ReadinessResponse(HealthResponse):
    database: dict[str, str] | None = None
