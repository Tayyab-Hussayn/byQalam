from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientError

from app.core.config import settings


@dataclass(frozen=True)
class AuthClaims:
    external_auth_id: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None


def decode_supabase_jwt(token: str) -> AuthClaims:
    if not settings.effective_supabase_jwks_url and not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "auth_not_configured",
                "message": "Supabase JWT verification is not configured.",
            },
        )

    try:
        payload = _decode_with_jwks(token)
    except HTTPException:
        raise
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_token",
                "message": "Invalid or expired authentication token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return _claims_from_payload(payload)


def _decode_with_jwks(token: str) -> dict[str, Any]:
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg")

    if algorithm == "HS256":
        return _decode_with_legacy_secret(token)

    if not settings.effective_supabase_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "jwks_not_configured",
                "message": "Supabase JWKS verification is not configured.",
            },
        )

    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
    except PyJWKClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "jwt_signing_key_not_found",
                "message": "JWT signing key could not be resolved from JWKS.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256", "RS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        options={"verify_iss": bool(settings.jwt_issuer)},
    )


def _decode_with_legacy_secret(token: str) -> dict[str, Any]:
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "legacy_jwt_secret_not_configured",
                "message": "Legacy Supabase JWT secret is not configured.",
            },
        )

    return jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        options={"verify_iss": bool(settings.jwt_issuer)},
    )


def _claims_from_payload(payload: dict[str, Any]) -> AuthClaims:
    external_auth_id = payload.get("sub")
    email = payload.get("email")
    if not external_auth_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_token_claims",
                "message": "Authentication token is missing required claims",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    metadata = _get_metadata(payload)
    return AuthClaims(
        external_auth_id=external_auth_id,
        email=email,
        full_name=metadata.get("full_name") or metadata.get("name"),
        avatar_url=metadata.get("avatar_url") or metadata.get("picture"),
    )


def _get_jwks_client() -> PyJWKClient:
    if not settings.effective_supabase_jwks_url:
        raise RuntimeError("Supabase JWKS URL is not configured.")
    return PyJWKClient(settings.effective_supabase_jwks_url, cache_keys=True)


def _get_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("user_metadata")
    return metadata if isinstance(metadata, dict) else {}
