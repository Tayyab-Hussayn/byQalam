"""posts workflow

Revision ID: 20260510_0003
Revises: 20260510_0002
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0003"
down_revision: str | None = "20260510_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("niche_slug", sa.String(length=120), nullable=True),
        sa.Column("title_internal", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("hashtags", sa.JSON(), nullable=False),
        sa.Column("first_comment", sa.Text(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("linkedin_target_type", sa.String(length=30), nullable=True),
        sa.Column("linkedin_target_urn", sa.String(length=255), nullable=True),
        sa.Column("linkedin_post_urn", sa.String(length=255), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("failure_reason", sa.String(length=500), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_posts_author_user_id"),
        "posts",
        ["author_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_linkedin_post_urn"),
        "posts",
        ["linkedin_post_urn"],
        unique=False,
    )
    op.create_index(op.f("ix_posts_niche_slug"), "posts", ["niche_slug"], unique=False)
    op.create_index(
        op.f("ix_posts_scheduled_for"),
        "posts",
        ["scheduled_for"],
        unique=False,
    )
    op.create_index(op.f("ix_posts_status"), "posts", ["status"], unique=False)
    op.create_index(
        "ix_posts_workspace_scheduled_for",
        "posts",
        ["workspace_id", "scheduled_for"],
        unique=False,
    )
    op.create_index(
        "ix_posts_workspace_status_created",
        "posts",
        ["workspace_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_workspace_id"),
        "posts",
        ["workspace_id"],
        unique=False,
    )

    op.create_table(
        "post_media",
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("media_type", sa.String(length=80), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_media_post_id"), "post_media", ["post_id"])

    op.create_table(
        "post_versions",
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("hashtags", sa.JSON(), nullable=False),
        sa.Column("first_comment", sa.Text(), nullable=True),
        sa.Column("change_reason", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_versions_post_id"), "post_versions", ["post_id"])

    op.create_table(
        "scheduled_posts",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id"),
    )
    op.create_index(
        op.f("ix_scheduled_posts_post_id"),
        "scheduled_posts",
        ["post_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_scheduled_posts_scheduled_for"),
        "scheduled_posts",
        ["scheduled_for"],
    )
    op.create_index(
        "ix_scheduled_posts_workspace_status_time",
        "scheduled_posts",
        ["workspace_id", "status", "scheduled_for"],
    )
    op.create_index(
        op.f("ix_scheduled_posts_workspace_id"),
        "scheduled_posts",
        ["workspace_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_scheduled_posts_workspace_id"), "scheduled_posts")
    op.drop_index("ix_scheduled_posts_workspace_status_time", "scheduled_posts")
    op.drop_index(op.f("ix_scheduled_posts_scheduled_for"), "scheduled_posts")
    op.drop_index(op.f("ix_scheduled_posts_post_id"), "scheduled_posts")
    op.drop_table("scheduled_posts")
    op.drop_index(op.f("ix_post_versions_post_id"), "post_versions")
    op.drop_table("post_versions")
    op.drop_index(op.f("ix_post_media_post_id"), "post_media")
    op.drop_table("post_media")
    op.drop_index(op.f("ix_posts_workspace_id"), "posts")
    op.drop_index("ix_posts_workspace_status_created", "posts")
    op.drop_index("ix_posts_workspace_scheduled_for", "posts")
    op.drop_index(op.f("ix_posts_status"), "posts")
    op.drop_index(op.f("ix_posts_scheduled_for"), "posts")
    op.drop_index(op.f("ix_posts_niche_slug"), "posts")
    op.drop_index(op.f("ix_posts_linkedin_post_urn"), "posts")
    op.drop_index(op.f("ix_posts_author_user_id"), "posts")
    op.drop_table("posts")
