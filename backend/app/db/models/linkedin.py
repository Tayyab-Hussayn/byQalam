from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import (
    LinkedinConnectionStatus,
    LinkedinPublishStatus,
    LinkedinTargetType,
)
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class LinkedinOAuthState(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "linkedin_oauth_states"
    __table_args__ = (
        Index("ix_linkedin_oauth_states_workspace_user", "workspace_id", "user_id"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    state_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    redirect_after: Mapped[str | None] = mapped_column(String(1024))
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(index=True)


class LinkedinConnection(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "linkedin_connections"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "target_urn",
            name="uq_linkedin_connections_workspace_target",
        ),
        Index(
            "ix_linkedin_connections_workspace_status",
            "workspace_id",
            "status",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    connected_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    target_type: Mapped[LinkedinTargetType] = mapped_column(
        Enum(
            LinkedinTargetType,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        nullable=False,
    )
    target_urn: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[LinkedinConnectionStatus] = mapped_column(
        Enum(
            LinkedinConnectionStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=LinkedinConnectionStatus.CONNECTED,
        nullable=False,
    )
    access_token_encrypted: Mapped[str] = mapped_column(Text)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(index=True)
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    token_key_id: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    publish_attempts = relationship(
        "LinkedinPublishAttempt",
        back_populates="connection",
    )


class LinkedinPublishAttempt(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "linkedin_publish_attempts"
    __table_args__ = (
        Index("ix_linkedin_publish_attempts_post_status", "post_id", "status"),
        Index(
            "ix_linkedin_publish_attempts_workspace_created",
            "workspace_id",
            "created_at",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        index=True,
    )
    connection_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("linkedin_connections.id", ondelete="SET NULL"),
        index=True,
    )
    status: Mapped[LinkedinPublishStatus] = mapped_column(
        Enum(
            LinkedinPublishStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=LinkedinPublishStatus.PENDING,
        nullable=False,
    )
    request_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    response_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    linkedin_post_urn: Mapped[str | None] = mapped_column(String(255), index=True)
    error_code: Mapped[str | None] = mapped_column(String(120))
    error_message: Mapped[str | None] = mapped_column(String(1000))

    connection = relationship("LinkedinConnection", back_populates="publish_attempts")
