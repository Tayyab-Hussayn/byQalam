"""notifications

Revision ID: 20260510_0008
Revises: 20260510_0007
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0008"
down_revision: str | None = "20260510_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=255), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_notifications_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index(
        "ix_notifications_workspace_created",
        "notifications",
        ["workspace_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_workspace_is_read",
        "notifications",
        ["workspace_id", "is_read"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_entity_type_entity_id",
        "notifications",
        ["entity_type", "entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_workspace_id"),
        "notifications",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_workspace_id"), "notifications")
    op.drop_index("ix_notifications_entity_type_entity_id", "notifications")
    op.drop_index("ix_notifications_workspace_is_read", "notifications")
    op.drop_index("ix_notifications_workspace_created", "notifications")
    op.drop_table("notifications")
