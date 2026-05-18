"""
Application Configuration
Manages all environment variables and settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


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
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:5173"],
        env="BACKEND_CORS_ORIGINS"
    )

    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")

    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_image_model: str = Field(default="dall-e-3", env="OPENAI_IMAGE_MODEL")

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

    # Qdrant Vector Store
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    @validator("backend_cors_origins", pre=True)
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
