from enum import StrEnum


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class SubscriptionStatus(StrEnum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"


class PlanInterval(StrEnum):
    MONTH = "month"
    YEAR = "year"


class UsageMetric(StrEnum):
    AI_GENERATION = "ai_generation"
    AI_REGENERATION = "ai_regeneration"
    SCHEDULED_POST = "scheduled_post"
    PUBLISHED_POST = "published_post"
    CONNECTED_LINKEDIN_ACCOUNT = "connected_linkedin_account"
    WORKSPACE_COUNT = "workspace_count"
    MEMBER_COUNT = "member_count"
    MEDIA_STORAGE_MB = "media_storage_mb"


class PostStatus(StrEnum):
    DRAFT = "draft"
    GENERATED = "generated"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PostSource(StrEnum):
    AI = "ai"
    CUSTOM = "custom"
    IMPORTED = "imported"


class LinkedinTargetType(StrEnum):
    MEMBER = "member"
    ORGANIZATION = "organization"


class LinkedinConnectionStatus(StrEnum):
    CONNECTED = "connected"
    REVOKED = "revoked"
    EXPIRED = "expired"
    FAILED = "failed"


class LinkedinPublishStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class GenerationStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
