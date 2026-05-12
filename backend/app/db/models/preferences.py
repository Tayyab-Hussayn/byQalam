from uuid import UUID

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class ContentPreference(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "content_preferences"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    niche_slug: Mapped[str | None] = mapped_column(String(120), index=True)
    target_audience: Mapped[str | None] = mapped_column(String(500))
    content_goals: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    tone: Mapped[str | None] = mapped_column(String(120))
    language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    post_style: Mapped[str | None] = mapped_column(String(120))
    cta_preference: Mapped[str | None] = mapped_column(String(120))
    hashtag_policy: Mapped[str | None] = mapped_column(String(120))
    emoji_policy: Mapped[str | None] = mapped_column(String(120))
    topics_to_avoid: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    preferred_post_length: Mapped[str | None] = mapped_column(String(80))

    workspace = relationship("Workspace")


class VoiceProfile(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "voice_profiles"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    summary: Mapped[str | None] = mapped_column(Text)
    traits: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    banned_phrases: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    sample_count: Mapped[int] = mapped_column(default=0, nullable=False)
    confidence_score: Mapped[int] = mapped_column(default=0, nullable=False)

    workspace = relationship("Workspace")


class WritingSample(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "writing_samples"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(120))

    workspace = relationship("Workspace")
    user = relationship("User")


class NicheProfile(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "niche_profiles"

    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text)
    audience_types: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    content_pillars: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    hook_patterns: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    cta_examples: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    risky_claims_to_avoid: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    hashtag_guidance: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
