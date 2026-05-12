import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_token_cipher
from app.db.models.enums import (
    LinkedinConnectionStatus,
    LinkedinPublishStatus,
    LinkedinTargetType,
    PostStatus,
    UsageMetric,
)
from app.db.models.linkedin import (
    LinkedinConnection,
    LinkedinOAuthState,
    LinkedinPublishAttempt,
)
from app.db.models.post import Post
from app.db.models.user import User
from app.services.audit import record_audit_event
from app.services.notifications import create_failure_notification
from app.services.usage import (
    assert_linkedin_connection_capacity,
    assert_quota_available,
    record_usage,
)

LINKEDIN_AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_POSTS_URL = "https://api.linkedin.com/rest/posts"


class LinkedinConfigError(RuntimeError):
    pass


class LinkedinOAuthError(RuntimeError):
    pass


def configured_scopes() -> list[str]:
    return [
        scope.strip()
        for scope in settings.linkedin_oauth_scopes.split()
        if scope.strip()
    ]


def hash_oauth_state(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


async def create_connect_url(
    session: AsyncSession,
    workspace_id: UUID,
    user: User,
    redirect_after: str | None,
) -> tuple[str, LinkedinOAuthState, str]:
    if not settings.linkedin_client_id:
        raise LinkedinConfigError("LINKEDIN_CLIENT_ID is not configured")

    raw_state = secrets.token_urlsafe(48)
    scopes = configured_scopes()
    state = LinkedinOAuthState(
        workspace_id=workspace_id,
        user_id=user.id,
        state_hash=hash_oauth_state(raw_state),
        redirect_after=redirect_after,
        scopes=scopes,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    session.add(state)
    await session.commit()
    await session.refresh(state)
    await record_audit_event(
        session,
        action="linkedin.connect.started",
        entity_type="linkedin_oauth_state",
        entity_id=str(state.id),
        workspace_id=workspace_id,
        actor_user_id=user.id,
    )
    await session.commit()

    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.linkedin_client_id,
            "redirect_uri": settings.linkedin_redirect_uri,
            "state": raw_state,
            "scope": " ".join(scopes),
        }
    )
    return f"{LINKEDIN_AUTHORIZE_URL}?{query}", state, raw_state


async def complete_oauth_callback(
    session: AsyncSession,
    raw_state: str,
    code: str,
) -> tuple[LinkedinConnection, LinkedinOAuthState]:
    if not settings.linkedin_client_id or not settings.linkedin_client_secret:
        raise LinkedinConfigError("LinkedIn OAuth credentials are not configured")

    state = await session.scalar(
        select(LinkedinOAuthState).where(
            LinkedinOAuthState.state_hash == hash_oauth_state(raw_state)
        )
    )
    if state is None or state.consumed_at is not None:
        raise LinkedinOAuthError("Invalid LinkedIn OAuth state")
    if state.expires_at < datetime.utcnow():
        raise LinkedinOAuthError("Expired LinkedIn OAuth state")

    token_data = await exchange_authorization_code(code)
    profile = await fetch_member_profile(token_data["access_token"])
    connection = await upsert_member_connection(
        session=session,
        state=state,
        token_data=token_data,
        profile=profile,
    )
    state.consumed_at = datetime.utcnow()
    await record_audit_event(
        session,
        action="linkedin.connected",
        entity_type="linkedin_connection",
        entity_id=str(connection.id),
        workspace_id=state.workspace_id,
        actor_user_id=state.user_id,
        metadata={"target_urn": connection.target_urn},
    )
    await session.commit()
    await session.refresh(connection)
    await session.refresh(state)
    return connection, state


async def exchange_authorization_code(code: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.linkedin_redirect_uri,
                "client_id": settings.linkedin_client_id,
                "client_secret": settings.linkedin_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code >= 400:
        raise LinkedinOAuthError(response.text[:500])
    data = response.json()
    if "access_token" not in data:
        raise LinkedinOAuthError("LinkedIn token response did not include access_token")
    return data


async def fetch_member_profile(access_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            LINKEDIN_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if response.status_code >= 400:
        raise LinkedinOAuthError(response.text[:500])
    return response.json()


async def upsert_member_connection(
    session: AsyncSession,
    state: LinkedinOAuthState,
    token_data: dict[str, Any],
    profile: dict[str, Any],
) -> LinkedinConnection:
    member_id = profile.get("sub")
    if not member_id:
        raise LinkedinOAuthError("LinkedIn profile response did not include subject")

    target_urn = f"urn:li:person:{member_id}"
    await assert_linkedin_connection_capacity(session, state.workspace_id)
    existing = await session.scalar(
        select(LinkedinConnection).where(
            LinkedinConnection.workspace_id == state.workspace_id,
            LinkedinConnection.target_urn == target_urn,
        )
    )
    cipher = get_token_cipher()
    expires_in = token_data.get("expires_in")
    expires_at = (
        datetime.utcnow() + timedelta(seconds=int(expires_in))
        if expires_in is not None
        else None
    )
    refresh_token = token_data.get("refresh_token")
    display_name = profile.get("name") or profile.get("email")
    scopes = token_data.get("scope", " ".join(state.scopes)).split()

    connection = existing or LinkedinConnection(
        workspace_id=state.workspace_id,
        connected_by_user_id=state.user_id,
        target_type=LinkedinTargetType.MEMBER,
        target_urn=target_urn,
    )
    connection.display_name = display_name
    connection.status = LinkedinConnectionStatus.CONNECTED
    connection.access_token_encrypted = cipher.encrypt(token_data["access_token"])
    connection.refresh_token_encrypted = (
        cipher.encrypt(refresh_token) if refresh_token else None
    )
    connection.token_expires_at = expires_at
    connection.scopes = scopes
    connection.token_key_id = settings.token_encryption_key_id
    connection.metadata_json = {"profile": profile}
    session.add(connection)
    await session.flush()
    return connection


async def list_connections(
    session: AsyncSession,
    workspace_id: UUID,
) -> list[LinkedinConnection]:
    result = await session.scalars(
        select(LinkedinConnection)
        .where(LinkedinConnection.workspace_id == workspace_id)
        .order_by(LinkedinConnection.created_at.desc())
    )
    return list(result.all())


async def disconnect_connection(
    session: AsyncSession,
    workspace_id: UUID,
    connection_id: UUID,
) -> LinkedinConnection | None:
    connection = await session.scalar(
        select(LinkedinConnection).where(
            LinkedinConnection.workspace_id == workspace_id,
            LinkedinConnection.id == connection_id,
        )
    )
    if connection is None:
        return None
    connection.status = LinkedinConnectionStatus.REVOKED
    connection.access_token_encrypted = ""
    connection.refresh_token_encrypted = None
    await record_audit_event(
        session,
        action="linkedin.disconnected",
        entity_type="linkedin_connection",
        entity_id=str(connection.id),
        workspace_id=workspace_id,
    )
    await session.commit()
    await session.refresh(connection)
    return connection


async def publish_text_post(
    session: AsyncSession,
    post: Post,
    connection: LinkedinConnection,
) -> LinkedinPublishAttempt:
    if post.status not in {
        PostStatus.APPROVED,
        PostStatus.SCHEDULED,
        PostStatus.PUBLISHING,
    }:
        raise ValueError("Only approved or scheduled posts can be published")
    if connection.status != LinkedinConnectionStatus.CONNECTED:
        raise ValueError("LinkedIn connection is not active")
    await assert_quota_available(session, post.workspace_id, UsageMetric.PUBLISHED_POST)

    request_json = build_text_post_payload(post, connection)
    attempt = LinkedinPublishAttempt(
        workspace_id=post.workspace_id,
        post_id=post.id,
        connection_id=connection.id,
        status=LinkedinPublishStatus.PENDING,
        request_json=request_json,
        response_json={},
    )
    session.add(attempt)
    await session.flush()

    try:
        post_urn, response_json = await create_linkedin_post(
            access_token=get_token_cipher().decrypt(connection.access_token_encrypted),
            payload=request_json,
        )
        attempt.status = LinkedinPublishStatus.SUCCEEDED
        attempt.linkedin_post_urn = post_urn
        attempt.response_json = response_json
        post.status = PostStatus.PUBLISHED
        post.linkedin_post_urn = post_urn
        await record_usage(session, post.workspace_id, UsageMetric.PUBLISHED_POST)
        await record_audit_event(
            session,
            action="linkedin.publish.succeeded",
            entity_type="linkedin_publish_attempt",
            entity_id=str(attempt.id),
            workspace_id=post.workspace_id,
            metadata={"post_id": str(post.id), "linkedin_post_urn": post_urn},
        )
    except Exception as exc:
        attempt.status = LinkedinPublishStatus.FAILED
        attempt.error_code = exc.__class__.__name__
        attempt.error_message = str(exc)[:1000]
        post.status = PostStatus.FAILED
        post.failure_reason = attempt.error_message
        await create_failure_notification(
            session,
            workspace_id=post.workspace_id,
            title="LinkedIn publish failed",
            body=attempt.error_message or "The LinkedIn publish request failed.",
            entity_type="linkedin_publish_attempt",
            entity_id=str(attempt.id),
            metadata={
                "post_id": str(post.id),
                "connection_id": str(connection.id),
                "error_code": attempt.error_code,
            },
        )
        await record_audit_event(
            session,
            action="linkedin.publish.failed",
            entity_type="linkedin_publish_attempt",
            entity_id=str(attempt.id),
            workspace_id=post.workspace_id,
            metadata={"post_id": str(post.id), "error": attempt.error_message},
        )
    await session.commit()
    await session.refresh(attempt)
    await session.refresh(post)
    return attempt


def build_text_post_payload(
    post: Post,
    connection: LinkedinConnection,
) -> dict[str, Any]:
    body = post.body
    if post.hashtags:
        body = f"{body}\n\n{' '.join(post.hashtags)}"
    return {
        "author": connection.target_urn,
        "commentary": body,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }


async def create_linkedin_post(
    access_token: str,
    payload: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            LINKEDIN_POSTS_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Linkedin-Version": settings.linkedin_api_version,
                "X-Restli-Protocol-Version": "2.0.0",
            },
        )
    if response.status_code >= 400:
        raise RuntimeError(response.text[:1000])
    post_urn = response.headers.get("x-restli-id")
    if not post_urn:
        raise RuntimeError("LinkedIn response did not include x-restli-id")
    return post_urn, {
        "status_code": response.status_code,
        "headers": dict(response.headers),
    }
