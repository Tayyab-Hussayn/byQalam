from cryptography.fernet import Fernet

from app.core.config import Settings

VALID_FERNET_KEY = Fernet.generate_key().decode()


def test_production_cors_rejects_localhost_origins() -> None:
    settings = Settings(
        app_env="production",
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/qalam",
        redis_url="redis://localhost:6379/0",
        encryption_key=VALID_FERNET_KEY,
        app_cors_origins="http://localhost:3000",
    )

    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        assert "APP_CORS_ORIGINS" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("production CORS should reject localhost origins")


def test_production_cors_accepts_real_origins() -> None:
    settings = Settings(
        app_env="production",
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/qalam",
        redis_url="redis://localhost:6379/0",
        encryption_key=VALID_FERNET_KEY,
        app_cors_origins="https://app.byqalam.com,https://www.byqalam.com",
    )

    settings.validate_runtime()


def test_production_requires_supabase_auth_config() -> None:
    settings = Settings(
        app_env="production",
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/qalam",
        redis_url="redis://localhost:6379/0",
        encryption_key=VALID_FERNET_KEY,
        app_cors_origins="https://app.byqalam.com",
        supabase_url=None,
        supabase_jwt_secret=None,
        supabase_jwks_url=None,
    )

    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        assert "SUPABASE_JWKS_URL or SUPABASE_JWT_SECRET" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("production auth config should be required")
