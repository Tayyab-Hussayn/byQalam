"""linkedin integration

Revision ID: 20260510_0005
Revises: 20260510_0004
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260510_0005"
down_revision: str | None = "20260510_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "linkedin_oauth_states",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("state_hash", sa.String(length=128), nullable=False),
        sa.Column("redirect_after", sa.String(length=1024), nullable=True),
        sa.Column("scopes", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_linkedin_oauth_states_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_linkedin_oauth_states_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_linkedin_oauth_states")),
    )
    op.create_index(
        op.f("ix_linkedin_oauth_states_state_hash"),
        "linkedin_oauth_states",
        ["state_hash"],
        unique=True,
    )
    op.create_index(
        "ix_linkedin_oauth_states_workspace_user",
        "linkedin_oauth_states",
        ["workspace_id", "user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_oauth_states_workspace_id"),
        "linkedin_oauth_states",
        ["workspace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_oauth_states_user_id"),
        "linkedin_oauth_states",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_oauth_states_expires_at"),
        "linkedin_oauth_states",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_oauth_states_consumed_at"),
        "linkedin_oauth_states",
        ["consumed_at"],
        unique=False,
    )

    op.create_table(
        "linkedin_connections",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("connected_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", sa.String(length=30), nullable=False),
        sa.Column("target_urn", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("access_token_encrypted", sa.Text(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("scopes", sa.JSON(), nullable=False),
        sa.Column("token_key_id", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["connected_by_user_id"],
            ["users.id"],
            name=op.f("fk_linkedin_connections_connected_by_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_linkedin_connections_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_linkedin_connections")),
        sa.UniqueConstraint(
            "workspace_id",
            "target_urn",
            name="uq_linkedin_connections_workspace_target",
        ),
    )
    op.create_index(
        "ix_linkedin_connections_workspace_status",
        "linkedin_connections",
        ["workspace_id", "status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_connections_workspace_id"),
        "linkedin_connections",
        ["workspace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_connections_target_urn"),
        "linkedin_connections",
        ["target_urn"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_connections_token_expires_at"),
        "linkedin_connections",
        ["token_expires_at"],
        unique=False,
    )

    op.create_table(
        "linkedin_publish_attempts",
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("connection_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("response_json", sa.JSON(), nullable=False),
        sa.Column("linkedin_post_urn", sa.String(length=255), nullable=True),
        sa.Column("error_code", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["linkedin_connections.id"],
            name=op.f("fk_linkedin_publish_attempts_connection_id_linkedin_connections"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
            name=op.f("fk_linkedin_publish_attempts_post_id_posts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_linkedin_publish_attempts_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_linkedin_publish_attempts")),
    )
    op.create_index(
        "ix_linkedin_publish_attempts_post_status",
        "linkedin_publish_attempts",
        ["post_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_linkedin_publish_attempts_workspace_created",
        "linkedin_publish_attempts",
        ["workspace_id", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_publish_attempts_workspace_id"),
        "linkedin_publish_attempts",
        ["workspace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_publish_attempts_post_id"),
        "linkedin_publish_attempts",
        ["post_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_publish_attempts_connection_id"),
        "linkedin_publish_attempts",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_linkedin_publish_attempts_linkedin_post_urn"),
        "linkedin_publish_attempts",
        ["linkedin_post_urn"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_linkedin_publish_attempts_linkedin_post_urn"),
        "linkedin_publish_attempts",
    )
    op.drop_index(
        op.f("ix_linkedin_publish_attempts_connection_id"),
        "linkedin_publish_attempts",
    )
    op.drop_index(
        op.f("ix_linkedin_publish_attempts_post_id"),
        "linkedin_publish_attempts",
    )
    op.drop_index(
        op.f("ix_linkedin_publish_attempts_workspace_id"),
        "linkedin_publish_attempts",
    )
    op.drop_index(
        "ix_linkedin_publish_attempts_workspace_created",
        "linkedin_publish_attempts",
    )
    op.drop_index(
        "ix_linkedin_publish_attempts_post_status",
        "linkedin_publish_attempts",
    )
    op.drop_table("linkedin_publish_attempts")

    op.drop_index(
        op.f("ix_linkedin_connections_token_expires_at"),
        "linkedin_connections",
    )
    op.drop_index(op.f("ix_linkedin_connections_target_urn"), "linkedin_connections")
    op.drop_index(op.f("ix_linkedin_connections_workspace_id"), "linkedin_connections")
    op.drop_index("ix_linkedin_connections_workspace_status", "linkedin_connections")
    op.drop_table("linkedin_connections")

    op.drop_index(op.f("ix_linkedin_oauth_states_consumed_at"), "linkedin_oauth_states")
    op.drop_index(op.f("ix_linkedin_oauth_states_expires_at"), "linkedin_oauth_states")
    op.drop_index(op.f("ix_linkedin_oauth_states_user_id"), "linkedin_oauth_states")
    op.drop_index(
        op.f("ix_linkedin_oauth_states_workspace_id"),
        "linkedin_oauth_states",
    )
    op.drop_index("ix_linkedin_oauth_states_workspace_user", "linkedin_oauth_states")
    op.drop_index(op.f("ix_linkedin_oauth_states_state_hash"), "linkedin_oauth_states")
    op.drop_table("linkedin_oauth_states")
