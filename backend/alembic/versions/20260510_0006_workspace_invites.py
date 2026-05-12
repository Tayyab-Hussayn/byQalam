"""workspace invites

Revision ID: 20260510_0006
Revises: 20260510_0005
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0006"
down_revision: str | None = "20260510_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workspace_invites",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("invited_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["invited_by_user_id"],
            ["users.id"],
            name=op.f("fk_workspace_invites_invited_by_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_workspace_invites_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspace_invites")),
        sa.UniqueConstraint("workspace_id", "email", name="uq_workspace_invites_email"),
        sa.UniqueConstraint("token_hash", name="uq_workspace_invites_token_hash"),
    )
    op.create_index(
        "ix_workspace_invites_workspace_email",
        "workspace_invites",
        ["workspace_id", "email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workspace_invites_workspace_id"),
        "workspace_invites",
        ["workspace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workspace_invites_email"),
        "workspace_invites",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workspace_invites_token_hash"),
        "workspace_invites",
        ["token_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workspace_invites_expires_at"),
        "workspace_invites",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_workspace_invites_expires_at"), "workspace_invites")
    op.drop_index(op.f("ix_workspace_invites_token_hash"), "workspace_invites")
    op.drop_index(op.f("ix_workspace_invites_email"), "workspace_invites")
    op.drop_index(op.f("ix_workspace_invites_workspace_id"), "workspace_invites")
    op.drop_index("ix_workspace_invites_workspace_email", "workspace_invites")
    op.drop_table("workspace_invites")
