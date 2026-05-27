"""Pytest conftest · env vars dummy para que `from app.config import settings`
no rompa al importar módulos de infraestructura. Mismo patrón que
application/tests/conftest.py. VOYAGE_API_KEY se deja SIN setear a propósito:
el estado por defecto (key ausente) es el que ejercitan los tests deploy-safe.
"""
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
