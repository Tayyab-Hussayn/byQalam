from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.health import check_database
from app.db.session import get_db_session
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        checked_at=datetime.now(UTC),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def ready(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReadinessResponse:
    try:
        database = await check_database(session)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_not_ready",
                "message": "Database connection failed",
            },
        ) from exc

    return ReadinessResponse(
        status="ready",
        service=settings.app_name,
        environment=settings.app_env,
        checked_at=datetime.now(UTC),
        database=database,
    )
