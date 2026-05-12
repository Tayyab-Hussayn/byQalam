from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException

from app.core import auth as auth_module
from app.core.auth import decode_supabase_jwt


def test_decode_supabase_jwt_uses_jwks_for_modern_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    monkeypatch.setattr(auth_module.settings, "supabase_url", "https://test.supabase.co")
    monkeypatch.setattr(auth_module.settings, "supabase_jwks_url", None)
    monkeypatch.setattr(auth_module.settings, "supabase_jwt_secret", None)
    monkeypatch.setattr(auth_module.settings, "jwt_audience", "authenticated")
    monkeypatch.setattr(auth_module.settings, "jwt_issuer", None)
    monkeypatch.setattr(
        auth_module,
        "_get_jwks_client",
        lambda: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=public_key)
        ),
    )
    token = jwt.encode(
        _payload(),
        private_key,
        algorithm="ES256",
        headers={"kid": "test-key"},
    )

    claims = decode_supabase_jwt(token)

    assert claims.external_auth_id == "auth-user-1"
    assert claims.email == "founder@byqalam.com"


def test_decode_supabase_jwt_supports_legacy_hs256_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-secret-that-is-long-enough-for-hs256"
    monkeypatch.setattr(auth_module.settings, "supabase_url", None)
    monkeypatch.setattr(auth_module.settings, "supabase_jwks_url", None)
    monkeypatch.setattr(auth_module.settings, "supabase_jwt_secret", secret)
    monkeypatch.setattr(auth_module.settings, "jwt_audience", "authenticated")
    monkeypatch.setattr(auth_module.settings, "jwt_issuer", None)
    token = jwt.encode(
        _payload(),
        secret,
        algorithm="HS256",
    )

    claims = decode_supabase_jwt(token)

    assert claims.external_auth_id == "auth-user-1"
    assert claims.email == "founder@byqalam.com"
    assert claims.full_name == "Qalam Founder"
    assert claims.avatar_url == "https://example.com/avatar.png"


def test_decode_supabase_jwt_rejects_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(auth_module.settings, "supabase_url", None)
    monkeypatch.setattr(auth_module.settings, "supabase_jwks_url", None)
    monkeypatch.setattr(
        auth_module.settings,
        "supabase_jwt_secret",
        "test-secret-that-is-long-enough-for-hs256",
    )
    monkeypatch.setattr(auth_module.settings, "jwt_audience", "authenticated")
    monkeypatch.setattr(auth_module.settings, "jwt_issuer", None)

    with pytest.raises(HTTPException) as exc:
        decode_supabase_jwt("not-a-token")

    assert exc.value.status_code == 401


def _payload() -> dict[str, object]:
    return {
        "sub": "auth-user-1",
        "email": "founder@byqalam.com",
        "aud": "authenticated",
        "exp": datetime.now(UTC) + timedelta(minutes=5),
        "user_metadata": {
            "full_name": "Qalam Founder",
            "avatar_url": "https://example.com/avatar.png",
        },
    }
