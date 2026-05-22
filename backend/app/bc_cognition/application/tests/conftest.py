"""Pytest conftest · setea env vars dummy para que `from app.config import
settings` no rompa al importar módulos que toquen infra Supabase.

Scope: solo este directorio de tests · no afecta prod ni otros tests.
Aplica antes de la colección porque pytest carga conftest primero.
"""
import os

_DUMMIES = {
    "SUPABASE_URL": "http://localhost:54321",
    "SUPABASE_ANON_KEY": "test_anon_key",
    "SUPABASE_SERVICE_ROLE_KEY": "test_service_role_key",
    "ANTHROPIC_API_KEY": "test_anthropic",
    "JWT_SECRET_KEY": "test_jwt_secret",
    "SECRET_KEY": "test_secret",
    "DATABASE_URL": "postgresql://test:test@localhost/test",  # DEBT-045
}
for _k, _v in _DUMMIES.items():
    os.environ.setdefault(_k, _v)
