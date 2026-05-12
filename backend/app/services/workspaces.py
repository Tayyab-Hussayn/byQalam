import hashlib
import re
import secrets
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import SubscriptionStatus, WorkspaceRole
from app.db.models.plan import Plan
from app.db.models.subscription import Subscription
from app.db.models.user import User
from app.db.models.workspace import Workspace, WorkspaceInvite, WorkspaceMember
from app.services.audit import record_audit_event
from app.services.usage import (
    assert_member_capacity,
    assert_workspace_capacity,
)


async def list_user_workspaces(
    session: AsyncSession,
    user: User,
) -> list[tuple[Workspace, WorkspaceRole]]:
    result = await session.execute(
        select(Workspace, WorkspaceMember.role)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(
            WorkspaceMember.user_id == user.id,
            WorkspaceMember.is_active.is_(True),
            Workspace.is_active.is_(True),
        )
        .order_by(Workspace.created_at.asc())
    )
    return list(result.all())


async def create_workspace(
    session: AsyncSession,
    user: User,
    name: str,
    timezone: str,
) -> Workspace:
    await assert_workspace_capacity(session, user.id)
    workspace = Workspace(
        name=name,
        slug=await generate_unique_slug(session, name),
        timezone=timezone,
    )
    session.add(workspace)
    await session.flush()

    session.add(
        WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER,
        )
    )

    free_plan = await session.scalar(select(Plan).where(Plan.slug == "free"))
    if free_plan is not None:
        session.add(
            Subscription(
                workspace_id=workspace.id,
                plan_id=free_plan.id,
                status=SubscriptionStatus.ACTIVE,
            )
        )

    await session.commit()
    await session.refresh(workspace)
    await record_audit_event(
        session,
        action="workspace.created",
        entity_type="workspace",
        entity_id=str(workspace.id),
        workspace_id=workspace.id,
        actor_user_id=user.id,
        metadata={"name": workspace.name, "timezone": workspace.timezone},
    )
    await session.commit()
    return workspace


async def list_workspace_members(
    session: AsyncSession,
    workspace_id: UUID,
) -> list[WorkspaceMember]:
    result = await session.scalars(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.is_active.is_(True),
        )
        .order_by(WorkspaceMember.created_at.asc())
    )
    return list(result.all())


async def list_workspace_invites(
    session: AsyncSession,
    workspace_id: UUID,
) -> list[WorkspaceInvite]:
    result = await session.scalars(
        select(WorkspaceInvite)
        .where(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.revoked_at.is_(None),
        )
        .order_by(WorkspaceInvite.created_at.desc())
    )
    return list(result.all())


async def create_workspace_invite(
    session: AsyncSession,
    workspace_id: UUID,
    invited_by_user: User,
    email: str,
    role: WorkspaceRole,
) -> tuple[WorkspaceInvite, str]:
    await assert_member_capacity(session, workspace_id, amount=1)
    raw_token = secrets.token_urlsafe(32)
    invite = WorkspaceInvite(
        workspace_id=workspace_id,
        invited_by_user_id=invited_by_user.id,
        email=email.lower().strip(),
        role=role,
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    await record_audit_event(
        session,
        action="workspace.invite.created",
        entity_type="workspace_invite",
        entity_id=str(invite.id),
        workspace_id=workspace_id,
        actor_user_id=invited_by_user.id,
        metadata={"email": invite.email, "role": invite.role.value},
    )
    await session.commit()
    return invite, raw_token


async def accept_workspace_invite(
    session: AsyncSession,
    user: User,
    raw_token: str,
) -> WorkspaceMember:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    invite = await session.scalar(
        select(WorkspaceInvite).where(
            WorkspaceInvite.token_hash == token_hash,
            WorkspaceInvite.revoked_at.is_(None),
        )
    )
    if invite is None:
        raise PermissionError("Workspace invite was not found")
    if invite.expires_at < datetime.utcnow():
        raise PermissionError("Workspace invite has expired")
    if invite.email.lower() != user.email.lower():
        raise PermissionError("Invite email does not match authenticated user")

    await assert_member_capacity(session, invite.workspace_id, amount=1)
    membership = await session.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == invite.workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if membership is None:
        membership = WorkspaceMember(
            workspace_id=invite.workspace_id,
            user_id=user.id,
            role=invite.role,
        )
        session.add(membership)
    else:
        membership.role = invite.role
        membership.is_active = True

    invite.accepted_at = datetime.utcnow()
    await record_audit_event(
        session,
        action="workspace.invite.accepted",
        entity_type="workspace_invite",
        entity_id=str(invite.id),
        workspace_id=invite.workspace_id,
        actor_user_id=user.id,
        metadata={"email": user.email, "role": invite.role.value},
    )
    await session.commit()
    await session.refresh(membership)
    await session.refresh(invite)
    return membership


async def update_workspace_member_role(
    session: AsyncSession,
    workspace_id: UUID,
    member_id: UUID,
    role: WorkspaceRole,
) -> WorkspaceMember | None:
    member = await session.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.id == member_id,
            WorkspaceMember.is_active.is_(True),
        )
    )
    if member is None:
        return None
    member.role = role
    await record_audit_event(
        session,
        action="workspace.member.role_updated",
        entity_type="workspace_member",
        entity_id=str(member.id),
        workspace_id=workspace_id,
        metadata={"role": role.value},
    )
    await session.commit()
    await session.refresh(member)
    return member


async def remove_workspace_member(
    session: AsyncSession,
    workspace_id: UUID,
    member_id: UUID,
) -> WorkspaceMember | None:
    member = await session.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.id == member_id,
            WorkspaceMember.is_active.is_(True),
        )
    )
    if member is None:
        return None
    member.is_active = False
    await record_audit_event(
        session,
        action="workspace.member.removed",
        entity_type="workspace_member",
        entity_id=str(member.id),
        workspace_id=workspace_id,
        metadata={"user_id": str(member.user_id)},
    )
    await session.commit()
    await session.refresh(member)
    return member


async def require_workspace_role(
    session: AsyncSession,
    user: User,
    workspace_id: UUID,
    allowed_roles: set[WorkspaceRole] | None = None,
) -> WorkspaceMember:
    query = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user.id,
        WorkspaceMember.is_active.is_(True),
    )
    membership = await session.scalar(query)
    if membership is None:
        raise PermissionError("Workspace membership is required")

    if allowed_roles and membership.role not in allowed_roles:
        raise PermissionError("Workspace role is not allowed")

    return membership


async def generate_unique_slug(session: AsyncSession, name: str) -> str:
    base_slug = slugify(name) or "workspace"
    slug = base_slug
    counter = 2

    while await session.scalar(select(Workspace.id).where(Workspace.slug == slug)):
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")[:100]
