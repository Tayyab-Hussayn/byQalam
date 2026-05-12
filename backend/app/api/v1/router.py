from fastapi import APIRouter

from app.api.v1 import (
    billing,
    generation,
    health,
    linkedin,
    me,
    posts,
    preferences,
    usage,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(me.router, tags=["me"])
api_router.include_router(workspaces.router, tags=["workspaces"])
api_router.include_router(preferences.router, tags=["preferences"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(generation.router, tags=["generation"])
api_router.include_router(linkedin.router, tags=["linkedin"])
api_router.include_router(billing.router, tags=["billing"])
api_router.include_router(usage.router, tags=["usage"])
