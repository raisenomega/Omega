"""
Application Configuration
Manages all environment variables and settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from app.bc_cognition.domain.routing_table import MODEL_SONNET  # P9 · string de modelo centralizado

class Settings(BaseSettings):
    """Application settings from environment variables"""
    # Application
    app_name: str = Field(default="OmegaRaisen", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    signup_enabled: bool = Field(default=False, env="SIGNUP_ENABLED")  # gate /register + /resellers/create (default cerrado en prod)
    secret_key: str = Field(..., env="SECRET_KEY")

    # API
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    # DEBT-026: campo str (no-complex) + property cors_origins_list (CSV · NoDecode no existe en 2.6.1)
    backend_cors_origins: str = Field(default="http://localhost:5173", env="BACKEND_CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> List[str]:
        """Lista parseada desde BACKEND_CORS_ORIGINS CSV. DEBT-026."""
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    database_url: str = Field(..., env="DATABASE_URL")  # DEBT-045 SQLAlchemyJobStore + DEBT-029 partial

    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    # Supabase JWT Secret · firma tokens Supabase Auth · vacío → get_current_user cae a JWT_SECRET_KEY local
    supabase_jwt_secret: str = Field(default="", env="SUPABASE_JWT_SECRET")

    # Anthropic Claude
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default=MODEL_SONNET, env="ANTHROPIC_MODEL")
    voyage_api_key: str = Field(default="", env="VOYAGE_API_KEY")  # DEBT-048 · embeddings ARIA (I1 exc 3)

    # JWT
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Stripe Payment
    stripe_secret_key: str = Field(default="", env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")
    stripe_price_basic: str = Field(default="", env="STRIPE_PRICE_BASIC")
    stripe_price_pro: str = Field(default="", env="STRIPE_PRICE_PRO")
    stripe_price_enterprise: str = Field(default="", env="STRIPE_PRICE_ENTERPRISE")
    # bc_billing/ checkout URLs · default dev local · override en Railway prod
    stripe_success_url: str = Field(default="http://localhost:5174/dashboard?upgraded=true", env="STRIPE_SUCCESS_URL")
    stripe_cancel_url: str = Field(default="http://localhost:5174/dashboard?upgrade_canceled=true", env="STRIPE_CANCEL_URL")
    stripe_price_aria_premium_client: str = Field(default="", env="STRIPE_PRICE_ARIA_PREMIUM_CLIENT")
    stripe_price_aria_premium_reseller: str = Field(default="", env="STRIPE_PRICE_ARIA_PREMIUM_RESELLER")
    stripe_price_video_pack_starter: str = Field(default="", env="STRIPE_PRICE_VIDEO_PACK_STARTER")
    stripe_price_video_pack_creator: str = Field(default="", env="STRIPE_PRICE_VIDEO_PACK_CREATOR")
    stripe_price_video_pack_cinematic_pro: str = Field(default="", env="STRIPE_PRICE_VIDEO_PACK_CINEMATIC_PRO")
    stripe_price_credit_pack_micro: str = Field(default="", env="STRIPE_PRICE_CREDIT_PACK_MICRO")  # DEBT-052 F4 credit packs
    stripe_price_credit_pack_starter: str = Field(default="", env="STRIPE_PRICE_CREDIT_PACK_STARTER")
    stripe_price_credit_pack_plus: str = Field(default="", env="STRIPE_PRICE_CREDIT_PACK_PLUS")
    stripe_price_credit_pack_ultra: str = Field(default="", env="STRIPE_PRICE_CREDIT_PACK_ULTRA")
    stripe_price_agent_publisher_esencial: str = Field(default="", env="STRIPE_PRICE_AGENT_PUBLISHER_ESENCIAL")  # DEBT-091
    stripe_price_agent_publisher_pro: str = Field(default="", env="STRIPE_PRICE_AGENT_PUBLISHER_PRO")
    stripe_price_agent_creative_esencial: str = Field(default="", env="STRIPE_PRICE_AGENT_CREATIVE_ESENCIAL")
    stripe_price_agent_creative_pro: str = Field(default="", env="STRIPE_PRICE_AGENT_CREATIVE_PRO")
    stripe_price_agent_trends_unico: str = Field(default="", env="STRIPE_PRICE_AGENT_TRENDS_UNICO")

    # Qdrant Vector Store
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # Rate Limiting · DEBT-070: per_minute lo consume RateLimitMiddleware (por IP · 300) · ajustable RATE_LIMIT_PER_MINUTE
    rate_limit_per_minute: int = Field(default=300, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")  # reservado · no consumido aún
    # Alertas SENTINEL (Optional → faltan = skip best-effort · Email RESEND · Telegram BOT_TOKEN+CHAT_ID)
    resend_api_key: Optional[str] = Field(default=None, env="RESEND_API_KEY")
    ipinfo_token: Optional[str] = Field(default=None, env="IPINFO_TOKEN")  # GUARDIAN geo · None = tokenless
    alert_email_to: str = Field(default="raisenagencypr@gmail.com", env="ALERT_EMAIL_TO")
    alert_email_from: str = Field(default="OMEGA SENTINEL <onboarding@resend.dev>", env="ALERT_EMAIL_FROM")
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # DEBT-027 · drops vite_*/db_url/etc. orphan env vars


# Global settings instance
settings = Settings()
