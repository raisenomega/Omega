"""
Application Configuration
Manages all environment variables and settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    app_name: str = Field(default="OmegaRaisen", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")

    # API
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    # DEBT-026: pydantic_settings 2.6.1 JSON-parsea List[str] antes de @validator
    # (NoDecode no existe en esta versión). Solución: campo str (no-complex) +
    # property `cors_origins_list` que expone el CSV parseado.
    backend_cors_origins: str = Field(
        default="http://localhost:5173",
        env="BACKEND_CORS_ORIGINS"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Lista parseada desde BACKEND_CORS_ORIGINS CSV. DEBT-026."""
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    database_url: str = Field(..., env="DATABASE_URL")  # DEBT-045 SQLAlchemyJobStore + DEBT-029 partial

    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    # Supabase JWT Secret · firma de los tokens emitidos por Supabase Auth.
    # Default vacío para no romper dev local · si vacío, get_current_user
    # cae al JWT_SECRET_KEY local (legacy /auth/login).
    supabase_jwt_secret: str = Field(default="", env="SUPABASE_JWT_SECRET")

    # Anthropic Claude
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        env="ANTHROPIC_MODEL"
    )

    # JWT
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        env="REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # Stripe Payment
    stripe_secret_key: str = Field(default="", env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")
    stripe_price_basic: str = Field(default="", env="STRIPE_PRICE_BASIC")
    stripe_price_pro: str = Field(default="", env="STRIPE_PRICE_PRO")
    stripe_price_enterprise: str = Field(default="", env="STRIPE_PRICE_ENTERPRISE")
    # bc_billing/ checkout URLs · default dev local · override en Railway prod
    stripe_success_url: str = Field(default="http://localhost:5174/dashboard?upgraded=true", env="STRIPE_SUCCESS_URL")
    stripe_cancel_url: str = Field(default="http://localhost:5174/dashboard?upgrade_canceled=true", env="STRIPE_CANCEL_URL")
    # ARIA Premium addon prices · DEBT-037 V1 (client) + DEBT-046 (reseller futuro)
    stripe_price_aria_premium_client: str = Field(default="", env="STRIPE_PRICE_ARIA_PREMIUM_CLIENT")
    stripe_price_aria_premium_reseller: str = Field(default="", env="STRIPE_PRICE_ARIA_PREMIUM_RESELLER")

    # Qdrant Vector Store
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # DEBT-027 · drops vite_*/db_url/etc. orphan env vars


# Global settings instance
settings = Settings()
