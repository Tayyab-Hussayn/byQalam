"""preferences onboarding

Revision ID: 20260510_0002
Revises: 20260510_0001
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0002"
down_revision: str | None = "20260510_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "content_preferences",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("niche_slug", sa.String(length=120), nullable=True),
        sa.Column("target_audience", sa.String(length=500), nullable=True),
        sa.Column("content_goals", sa.JSON(), nullable=False),
        sa.Column("tone", sa.String(length=120), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("post_style", sa.String(length=120), nullable=True),
        sa.Column("cta_preference", sa.String(length=120), nullable=True),
        sa.Column("hashtag_policy", sa.String(length=120), nullable=True),
        sa.Column("emoji_policy", sa.String(length=120), nullable=True),
        sa.Column("topics_to_avoid", sa.JSON(), nullable=False),
        sa.Column("preferred_post_length", sa.String(length=80), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id"),
    )
    op.create_index(
        op.f("ix_content_preferences_niche_slug"),
        "content_preferences",
        ["niche_slug"],
        unique=False,
    )
    op.create_index(
        op.f("ix_content_preferences_workspace_id"),
        "content_preferences",
        ["workspace_id"],
        unique=True,
    )

    op.create_table(
        "niche_profiles",
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("audience_types", sa.JSON(), nullable=False),
        sa.Column("content_pillars", sa.JSON(), nullable=False),
        sa.Column("hook_patterns", sa.JSON(), nullable=False),
        sa.Column("cta_examples", sa.JSON(), nullable=False),
        sa.Column("risky_claims_to_avoid", sa.JSON(), nullable=False),
        sa.Column("hashtag_guidance", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_niche_profiles_slug"),
        "niche_profiles",
        ["slug"],
        unique=True,
    )

    op.create_table(
        "voice_profiles",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("traits", sa.JSON(), nullable=False),
        sa.Column("banned_phrases", sa.JSON(), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id"),
    )
    op.create_index(
        op.f("ix_voice_profiles_workspace_id"),
        "voice_profiles",
        ["workspace_id"],
        unique=True,
    )

    op.create_table(
        "writing_samples",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_writing_samples_user_id"),
        "writing_samples",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_writing_samples_workspace_id"),
        "writing_samples",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_writing_samples_workspace_id"), "writing_samples")
    op.drop_index(op.f("ix_writing_samples_user_id"), "writing_samples")
    op.drop_table("writing_samples")
    op.drop_index(op.f("ix_voice_profiles_workspace_id"), "voice_profiles")
    op.drop_table("voice_profiles")
    op.drop_index(op.f("ix_niche_profiles_slug"), "niche_profiles")
    op.drop_table("niche_profiles")
    op.drop_index(op.f("ix_content_preferences_workspace_id"), "content_preferences")
    op.drop_index(op.f("ix_content_preferences_niche_slug"), "content_preferences")
    op.drop_table("content_preferences")
