"""Regresión SEGURIDAD: get_current_user NUNCA confía en user_metadata.role del JWT.

El role se DERIVA server-side de la DB (resellers.is_owner · commit 33166e4 · forgery-proof).
Un usuario que se auto-asigna role='owner' en user_metadata (escribible client-side) sigue
siendo lo que diga la DB. Estos tests fallan si alguien reintroduce el claim como fuente de role.
"""
import asyncio
from app.api.routes.auth import auth_utils


class _Resp:
    def __init__(self, data): self.data = data


class _Query:
    def __init__(self, data): self._d = data
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def execute(self): return _Resp(self._d)


class _Client:
    def __init__(self, data): self._d = data
    def table(self, *a, **k): return _Query(self._d)


class _Service:
    def __init__(self, data): self.client = _Client(data)


def _setup(monkeypatch, forged_role, db_rows):
    """Token con user_metadata.role=forged_role (forja) · la DB resellers devuelve db_rows."""
    monkeypatch.setattr(auth_utils, "_role_cache", {})  # cache limpio por test
    monkeypatch.setattr(auth_utils, "_decode_supabase", lambda token: {
        "sub": "u-test", "email": "x@y.com", "user_metadata": {"role": forged_role}})
    monkeypatch.setattr("app.infrastructure.supabase_service.get_supabase_service",
                        lambda: _Service(db_rows))


def test_user_metadata_owner_ignored_when_db_says_client(monkeypatch):
    """user_metadata='owner' + DB sin fila reseller → role='client' (forja IGNORADA)."""
    _setup(monkeypatch, forged_role="owner", db_rows=[])
    user = asyncio.run(auth_utils.get_current_user("Bearer faketoken"))
    assert user["role"] == "client"  # NO 'owner' del claim
    assert user["id"] == "u-test"


def test_db_is_owner_true_wins(monkeypatch):
    """DB reseller is_owner=true → role='owner' (la verdad viene de la DB, no del claim)."""
    _setup(monkeypatch, forged_role="client", db_rows=[{"id": "r-1", "is_owner": True}])
    assert asyncio.run(auth_utils.get_current_user("Bearer x"))["role"] == "owner"


def test_db_reseller_not_owner_despite_metadata_owner(monkeypatch):
    """DB reseller is_owner=false → role='reseller' aunque user_metadata mienta 'owner'."""
    _setup(monkeypatch, forged_role="owner", db_rows=[{"id": "r-2", "is_owner": False}])
    assert asyncio.run(auth_utils.get_current_user("Bearer x"))["role"] == "reseller"
