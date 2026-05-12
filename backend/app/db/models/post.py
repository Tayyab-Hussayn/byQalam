from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import LinkedinTargetType, PostSource, PostStatus
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class Post(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index(
            "ix_posts_workspace_status_created",
            "workspace_id",
            "status",
            "created_at",
        ),
        Index("ix_posts_workspace_scheduled_for", "workspace_id", "scheduled_for"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    author_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[PostStatus] = mapped_column(
        Enum(
            PostStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=PostStatus.DRAFT,
        index=True,
        nullable=False,
    )
    source: Mapped[PostSource] = mapped_column(
        Enum(
            PostSource,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=PostSource.CUSTOM,
        nullable=False,
    )
    niche_slug: Mapped[str | None] = mapped_column(String(120), index=True)
    title_internal: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    first_comment: Mapped[str | None] = mapped_column(Text)
    scheduled_for: Mapped[datetime | None] = mapped_column(index=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    linkedin_target_type: Mapped[LinkedinTargetType | None] = mapped_column(
        Enum(
            LinkedinTargetType,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        )
    )
    linkedin_target_urn: Mapped[str | None] = mapped_column(String(255))
    linkedin_post_urn: Mapped[str | None] = mapped_column(String(255), index=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(500))
    failure_reason: Mapped[str | None] = mapped_column(String(500))

    versions = relationship(
        "PostVersion",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    media = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class PostVersion(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "post_versions"

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
    )
    version_number: Mapped[int] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    first_comment: Mapped[str | None] = mapped_column(Text)
    change_reason: Mapped[str | None] = mapped_column(String(255))

    post = relationship("Post", back_populates="versions")


class PostMedia(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "post_media"

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
    )
    storage_path: Mapped[str] = mapped_column(String(1024))
    media_type: Mapped[str] = mapped_column(String(80))
    original_filename: Mapped[str | None] = mapped_column(String(255))
    size_bytes: Mapped[int | None] = mapped_column()

    post = relationship("Post", back_populates="media")


class ScheduledPost(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scheduled_posts"
    __table_args__ = (
        Index(
            "ix_scheduled_posts_workspace_status_time",
            "workspace_id",
            "status",
            "scheduled_for",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    status: Mapped[PostStatus] = mapped_column(
        Enum(
            PostStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=PostStatus.SCHEDULED,
        nullable=False,
    )
    scheduled_for: Mapped[datetime] = mapped_column(index=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)

    post = relationship("Post")
