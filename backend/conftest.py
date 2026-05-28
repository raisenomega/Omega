"""Pytest conftest raíz del backend · setea env vars dummy para que
`from app.config import settings` no rompa al colectar CUALQUIER test.

Antes solo 3 dirs de tests tenían conftest local; los demás (agents/,
billing/) rompían la colección sin env exportado, y el CHECK 9 del gate
(pytest desde backend/) fallaba o quedaba frágil al entorno. Este conftest
raíz cubre toda la suite. `setdefault` → no pisa env real si ya existe.
Scope: solo tests · no afecta prod.
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
