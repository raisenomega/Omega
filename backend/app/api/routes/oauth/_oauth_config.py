"""OAuth provider config (RONDA D). Settings SEPARADO para no inflar config.py (techo C4
100L). Lee del mismo .env via pydantic-settings (no os.getenv · DEBT-029). Cualquier
credencial vacía → el flujo del proveedor responde 503 honesto (sin app registrada)."""
from pydantic_settings import BaseSettings
from pydantic import Field


class OAuthSettings(BaseSettings):
    """Credenciales OAuth · vacías por default (503 honesto hasta que el owner las cargue)."""
    meta_app_id: str = Field(default="", env="META_APP_ID")
    meta_app_secret: str = Field(default="", env="META_APP_SECRET")
    google_client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    oauth_redirect_base: str = Field(default="http://localhost:8000", env="OAUTH_REDIRECT_BASE")
    oauth_encryption_key: str = Field(default="", env="OAUTH_ENCRYPTION_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


_oauth_settings: "OAuthSettings | None" = None


def get_oauth_settings() -> OAuthSettings:
    """Lazy singleton."""
    global _oauth_settings
    if _oauth_settings is None:
        _oauth_settings = OAuthSettings()
    return _oauth_settings
