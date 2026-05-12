"""ai generation

Revision ID: 20260510_0004
Revises: 20260510_0003
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0004"
down_revision: str | None = "20260510_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prompt_templates",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("user_prompt_template", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prompt_templates_name"), "prompt_templates", ["name"])
    op.create_index(
        op.f("ix_prompt_templates_version"),
        "prompt_templates",
        ["version"],
    )

    op.create_table(
        "ai_generation_runs",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("prompt_template_name", sa.String(length=120), nullable=True),
        sa.Column("prompt_template_version", sa.String(length=40), nullable=True),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=True),
        sa.Column("tokens_input", sa.Integer(), nullable=True),
        sa.Column("tokens_output", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_cents", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_generation_runs_post_id"),
        "ai_generation_runs",
        ["post_id"],
    )
    op.create_index(
        "ix_ai_generation_runs_workspace_created",
        "ai_generation_runs",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        op.f("ix_ai_generation_runs_workspace_id"),
        "ai_generation_runs",
        ["workspace_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_generation_runs_workspace_id"), "ai_generation_runs")
    op.drop_index("ix_ai_generation_runs_workspace_created", "ai_generation_runs")
    op.drop_index(op.f("ix_ai_generation_runs_post_id"), "ai_generation_runs")
    op.drop_table("ai_generation_runs")
    op.drop_index(op.f("ix_prompt_templates_version"), "prompt_templates")
    op.drop_index(op.f("ix_prompt_templates_name"), "prompt_templates")
    op.drop_table("prompt_templates")
