"""Feature flags · settings SEPARADO (no inflar config.py · techo C4 100L · DEBT-029).
Lee del mismo .env via pydantic-settings (patrón de _oauth_config/zernio_config). Default seguro."""
from pydantic_settings import BaseSettings
from pydantic import Field


class FeatureFlags(BaseSettings):
    """Flags de rollout · default OFF = reversibilidad total (apagás la env var → comportamiento viejo)."""
    image_async_enabled: bool = Field(default=False, env="IMAGE_ASYNC_ENABLED")  # DEBT-IMAGE-ASYNC F3

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


_flags: "FeatureFlags | None" = None


def get_feature_flags() -> FeatureFlags:
    """Lazy singleton (mismo patrón que get_oauth_settings/get_zernio_settings)."""
    global _flags
    if _flags is None:
        _flags = FeatureFlags()
    return _flags
