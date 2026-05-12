from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import WorkspaceRole
from app.db.models.mixins import TimestampMixin, UuidPrimaryKeyMixin


class Workspace(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    members = relationship("WorkspaceMember", back_populates="workspace")
    subscription = relationship("Subscription", back_populates="workspace")
    invites = relationship("WorkspaceInvite", back_populates="workspace")


class WorkspaceMember(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_members_member"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        Enum(
            WorkspaceRole,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=WorkspaceRole.OWNER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="memberships")


class WorkspaceInvite(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspace_invites"
    __table_args__ = (
        UniqueConstraint("workspace_id", "email", name="uq_workspace_invites_email"),
        UniqueConstraint("token_hash", name="uq_workspace_invites_token_hash"),
        Index("ix_workspace_invites_workspace_email", "workspace_id", "email"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    invited_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    email: Mapped[str] = mapped_column(String(320), index=True)
    role: Mapped[WorkspaceRole] = mapped_column(
        Enum(
            WorkspaceRole,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
            length=30,
        ),
        default=WorkspaceRole.VIEWER,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(128), index=True)
    expires_at: Mapped[datetime] = mapped_column(index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(index=True)

    workspace = relationship("Workspace", back_populates="invites")
