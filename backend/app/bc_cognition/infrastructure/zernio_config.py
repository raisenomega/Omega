"""Zernio config · settings SEPARADO para NO inflar config.py (techo C4 100L · DEBT-029).
Lee del mismo .env via pydantic-settings (patrón espejo de _oauth_config.py). Key vacía →
el adapter levanta error honesto (regla cero-mocks · nunca finge una publicación)."""
from pydantic_settings import BaseSettings
from pydantic import Field


class ZernioSettings(BaseSettings):
    """Credencial + base URL de Zernio · key vacía por default (sin publicar hasta cargarla)."""
    zernio_api_key: str = Field(default="", env="ZERNIO_API_KEY")
    zernio_api_base: str = Field(default="https://zernio.com/api/v1", env="ZERNIO_API_BASE")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


_zernio_settings: "ZernioSettings | None" = None


def get_zernio_settings() -> ZernioSettings:
    """Lazy singleton (mismo patrón que get_oauth_settings)."""
    global _zernio_settings
    if _zernio_settings is None:
        _zernio_settings = ZernioSettings()
    return _zernio_settings
