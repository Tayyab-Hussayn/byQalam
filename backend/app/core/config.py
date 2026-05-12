from functools import lru_cache
from typing import Literal

from cryptography.fernet import Fernet
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["local", "test", "staging", "production"]
AiProvider = Literal["mock", "openai", "anthropic", "google", "groq", "mistral"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: AppEnv = "local"
    app_name: str = "Qalam API"
    app_debug: bool = False
    app_api_prefix: str = "/api/v1"
    app_frontend_url: str = "http://localhost:3000"
    app_cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/qalam"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_connect_timeout_seconds: int = 10

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    supabase_url: str | None = None
    supabase_jwks_url: str | None = None
    supabase_publishable_key: str | None = None
    supabase_secret_key: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_service_role_key: str | None = None
    supabase_storage_bucket: str = "qalam-media"

    jwt_audience: str = "authenticated"
    jwt_issuer: str | None = None
    cookie_domain: str | None = None

    encryption_key: str = "replace-with-fernet-key"
    token_encryption_key_id: str = "local"

    ai_default_provider: AiProvider = "mock"
    ai_default_model: str = "mock-qalam-v1"
    ai_fallback_provider: AiProvider | None = None
    ai_request_timeout_seconds: int = 60
    ai_max_retries: int = 2
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_ai_api_key: str | None = None
    groq_api_key: str | None = None
    mistral_api_key: str | None = None

    linkedin_client_id: str | None = None
    linkedin_client_secret: str | None = None
    linkedin_redirect_uri: str = (
        "http://localhost:8000/api/v1/linkedin/oauth/callback"
    )
    linkedin_oauth_scopes: str = "openid profile email w_member_social"
    linkedin_api_version: str = "202604"

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_starter: str | None = None
    stripe_price_pro: str | None = None
    stripe_price_agency: str | None = None

    sentry_dsn: str | None = None
    log_level: str = "INFO"
    rate_limit_backend: str = "redis"
    rate_limit_requests_per_minute: int = 120

    enable_linkedin_publishing: bool = False
    enable_linkedin_company_pages: bool = False
    enable_media_uploads: bool = False
    enable_stripe_billing: bool = False
    enable_ai_generation: bool = True
    enable_background_generation: bool = False
    enable_rate_limiting: bool = True

    free_monthly_ai_generations: int = 20
    free_monthly_scheduled_posts: int = 5
    free_max_workspaces: int = 1
    free_max_members: int = 1
    free_max_linkedin_connections: int = 0
    free_media_storage_mb: int = 50

    starter_monthly_ai_generations: int = 300
    starter_monthly_scheduled_posts: int = 100
    starter_max_workspaces: int = 1
    starter_max_members: int = 2
    starter_max_linkedin_connections: int = 1
    starter_media_storage_mb: int = 500

    pro_monthly_ai_generations: int = 1000
    pro_monthly_scheduled_posts: int = 500
    pro_max_workspaces: int = 3
    pro_max_members: int = 5
    pro_max_linkedin_connections: int = 3
    pro_media_storage_mb: int = 5000

    agency_monthly_ai_generations: int = 5000
    agency_monthly_scheduled_posts: int = 2500
    agency_max_workspaces: int = 50
    agency_max_members: int = 25
    agency_max_linkedin_connections: int = 50
    agency_media_storage_mb: int = 50000

    @field_validator(
        "supabase_url",
        "supabase_jwks_url",
        "supabase_publishable_key",
        "supabase_secret_key",
        "supabase_jwt_secret",
        "supabase_service_role_key",
        "jwt_issuer",
        "cookie_domain",
        "ai_fallback_provider",
        "openai_api_key",
        "anthropic_api_key",
        "google_ai_api_key",
        "groq_api_key",
        "mistral_api_key",
        "linkedin_client_id",
        "linkedin_client_secret",
        "stripe_secret_key",
        "stripe_webhook_secret",
        "stripe_price_starter",
        "stripe_price_pro",
        "stripe_price_agency",
        "sentry_dsn",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.app_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def effective_supabase_jwks_url(self) -> str | None:
        if self.supabase_jwks_url:
            return self.supabase_jwks_url
        if self.supabase_url:
            return (
                self.supabase_url.rstrip("/")
                + "/auth/v1/.well-known/jwks.json"
            )
        return None

    @property
    def effective_supabase_admin_key(self) -> str | None:
        return self.supabase_secret_key or self.supabase_service_role_key

    def validate_runtime(self) -> None:
        if self.app_env == "production":
            missing = []
            if not self.database_url:
                missing.append("DATABASE_URL")
            if not self.redis_url:
                missing.append("REDIS_URL")
            if not self.app_cors_origins.strip():
                missing.append("APP_CORS_ORIGINS")
            if any(
                "localhost" in origin or "127.0.0.1" in origin or origin == "*"
                for origin in self.cors_origins
            ):
                missing.append("APP_CORS_ORIGINS must not include local origins")
            if self.encryption_key == "replace-with-fernet-key":
                missing.append("ENCRYPTION_KEY")
            else:
                try:
                    Fernet(self.encryption_key.encode())
                except (ValueError, TypeError):
                    missing.append("ENCRYPTION_KEY must be a valid Fernet key")
            if not self.effective_supabase_jwks_url and not self.supabase_jwt_secret:
                missing.append("SUPABASE_JWKS_URL or SUPABASE_JWT_SECRET")
            if self.ai_default_provider != "mock" and not self.provider_api_key:
                missing.append(f"{self.ai_default_provider.upper()}_API_KEY")
            if missing:
                joined = ", ".join(missing)
                raise RuntimeError(f"Missing production configuration: {joined}")

    @property
    def provider_api_key(self) -> str | None:
        return {
            "mock": "mock",
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_ai_api_key,
            "groq": self.groq_api_key,
            "mistral": self.mistral_api_key,
        }[self.ai_default_provider]


@lru_cache
def get_settings() -> Settings:
    loaded = Settings()
    loaded.validate_runtime()
    return loaded


settings = get_settings()
