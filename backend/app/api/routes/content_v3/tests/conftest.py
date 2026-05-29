"""Env dummy para importar handlers content_v3 sin romper config. Mismo patrón que
bc_cognition/infrastructure/tests/conftest.py."""
import os

_DUMMIES = {
    "SUPABASE_URL": "http://localhost:54321",
    "SUPABASE_ANON_KEY": "test_anon_key",
    "SUPABASE_SERVICE_ROLE_KEY": "test_service_role_key",
    "ANTHROPIC_API_KEY": "test_anthropic",
    "JWT_SECRET_KEY": "test_jwt_secret",
    "SECRET_KEY": "test_secret",
    "DATABASE_URL": "postgresql://test:test@localhost/test",
}
for _k, _v in _DUMMIES.items():
    os.environ.setdefault(_k, _v)
