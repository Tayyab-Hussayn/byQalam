"""dead letter jobs

Revision ID: 20260510_0009
Revises: 20260510_0008
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0009"
down_revision: str | None = "20260510_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dead_letter_jobs",
        sa.Column("task_name", sa.String(length=255), nullable=False),
        sa.Column("task_id", sa.String(length=255), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=255), nullable=True),
        sa.Column("retries", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("error_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_dead_letter_jobs_workspace_id_workspaces"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dead_letter_jobs")),
    )
    op.create_index(
        "ix_dead_letter_jobs_task_name_created",
        "dead_letter_jobs",
        ["task_name", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_dead_letter_jobs_workspace_created",
        "dead_letter_jobs",
        ["workspace_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_dead_letter_jobs_entity_type_entity_id",
        "dead_letter_jobs",
        ["entity_type", "entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dead_letter_jobs_task_id"),
        "dead_letter_jobs",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dead_letter_jobs_workspace_id"),
        "dead_letter_jobs",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_dead_letter_jobs_workspace_id"), "dead_letter_jobs")
    op.drop_index(op.f("ix_dead_letter_jobs_task_id"), "dead_letter_jobs")
    op.drop_index("ix_dead_letter_jobs_entity_type_entity_id", "dead_letter_jobs")
    op.drop_index("ix_dead_letter_jobs_workspace_created", "dead_letter_jobs")
    op.drop_index("ix_dead_letter_jobs_task_name_created", "dead_letter_jobs")
    op.drop_table("dead_letter_jobs")
