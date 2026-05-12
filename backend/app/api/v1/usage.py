from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.usage import UsageItemResponse, UsageSummaryResponse
from app.services.usage import build_usage_summary
from app.services.workspaces import require_workspace_role

router = APIRouter(prefix="/workspaces/{workspace_id}/usage")


@router.get("", response_model=UsageSummaryResponse)
async def read_usage_summary(
    workspace_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UsageSummaryResponse:
    try:
        await require_workspace_role(session, current_user.user, workspace_id)
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "workspace_forbidden",
                "message": "Workspace access is required.",
            },
        ) from exc

    summary = await build_usage_summary(session, workspace_id)
    return UsageSummaryResponse(
        plan_slug=summary.plan_slug,
        period_start=summary.period_start,
        period_end=summary.period_end,
        items=[
            UsageItemResponse(
                metric=item.metric,
                used=item.used,
                limit=item.limit,
            )
            for item in summary.items
        ],
    )
