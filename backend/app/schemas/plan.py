from pydantic import BaseModel


class PlanQuota(BaseModel):
    monthly_ai_generations: int
    monthly_scheduled_posts: int
    max_workspaces: int
    max_members: int
    max_linkedin_connections: int
    media_storage_mb: int


class PlanSeed(BaseModel):
    slug: str
    name: str
    sort_order: int
    stripe_price_id: str | None = None
    quotas: PlanQuota
