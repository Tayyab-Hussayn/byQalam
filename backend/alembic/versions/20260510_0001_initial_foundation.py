"""initial foundation

Revision ID: 20260510_0001
Revises:
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("interval", sa.String(length=20), nullable=False),
        sa.Column("stripe_price_id", sa.String(length=255), nullable=True),
        sa.Column("quotas", sa.JSON(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("stripe_price_id"),
    )
    op.create_index(op.f("ix_plans_slug"), "plans", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("external_auth_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("external_auth_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(
        op.f("ix_users_external_auth_id"),
        "users",
        ["external_auth_id"],
        unique=True,
    )

    op.create_table(
        "workspaces",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_workspaces_slug"), "workspaces", ["slug"], unique=True)

    op.create_table(
        "subscriptions",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_subscription_id"),
        sa.UniqueConstraint("workspace_id"),
    )
    op.create_index(
        op.f("ix_subscriptions_plan_id"),
        "subscriptions",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_stripe_customer_id"),
        "subscriptions",
        ["stripe_customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_workspace_id"),
        "subscriptions",
        ["workspace_id"],
        unique=True,
    )

    op.create_table(
        "usage_ledger",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("metric", sa.String(length=80), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_usage_ledger_metric"),
        "usage_ledger",
        ["metric"],
        unique=False,
    )
    op.create_index(
        op.f("ix_usage_ledger_period_end"),
        "usage_ledger",
        ["period_end"],
        unique=False,
    )
    op.create_index(
        op.f("ix_usage_ledger_period_start"),
        "usage_ledger",
        ["period_start"],
        unique=False,
    )
    op.create_index(
        "ix_usage_ledger_workspace_metric_period",
        "usage_ledger",
        ["workspace_id", "metric", "period_start", "period_end"],
        unique=False,
    )
    op.create_index(
        op.f("ix_usage_ledger_workspace_id"),
        "usage_ledger",
        ["workspace_id"],
        unique=False,
    )

    op.create_table(
        "workspace_members",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_workspace_members_member",
        ),
    )
    op.create_index(
        op.f("ix_workspace_members_user_id"),
        "workspace_members",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workspace_members_workspace_id"),
        "workspace_members",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_workspace_members_workspace_id"), "workspace_members")
    op.drop_index(op.f("ix_workspace_members_user_id"), "workspace_members")
    op.drop_table("workspace_members")
    op.drop_index(op.f("ix_usage_ledger_workspace_id"), "usage_ledger")
    op.drop_index("ix_usage_ledger_workspace_metric_period", "usage_ledger")
    op.drop_index(op.f("ix_usage_ledger_period_start"), "usage_ledger")
    op.drop_index(op.f("ix_usage_ledger_period_end"), "usage_ledger")
    op.drop_index(op.f("ix_usage_ledger_metric"), "usage_ledger")
    op.drop_table("usage_ledger")
    op.drop_index(op.f("ix_subscriptions_workspace_id"), "subscriptions")
    op.drop_index(op.f("ix_subscriptions_stripe_customer_id"), "subscriptions")
    op.drop_index(op.f("ix_subscriptions_plan_id"), "subscriptions")
    op.drop_table("subscriptions")
    op.drop_index(op.f("ix_workspaces_slug"), "workspaces")
    op.drop_table("workspaces")
    op.drop_index(op.f("ix_users_external_auth_id"), "users")
    op.drop_index(op.f("ix_users_email"), "users")
    op.drop_table("users")
    op.drop_index(op.f("ix_plans_slug"), "plans")
    op.drop_table("plans")
