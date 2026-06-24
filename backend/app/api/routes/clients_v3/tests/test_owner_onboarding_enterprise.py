"""Tests · Commit 4 · negocio nuevo de cuenta-dueño nace Enterprise perpetuo (espejo migr 00075).

Cuenta en owner_accounts (00074) crea negocio vía onboarding → client_plans se promueve a
enterprise/2099 (client_plans = fuente del gate · useClientPlanStatus.plan). Cuenta normal →
no-op (default/trial · sin cambio). El flag SOLO decide el plan: NUNCA toca la tabla clients
→ ownership intacto (clients.user_id · resolve_client_or_403 ajenos a esto).
"""
import asyncio
from types import SimpleNamespace

import pytest

import app.api.routes.clients_v3.handlers.create_client_onboarding as handler
import app.api.routes.clients_v3._clients_repository as repo
import app.bc_cognition.infrastructure.owner_accounts_repository as owners
from app.api.routes.clients_v3.models.onboarding import OnboardingPayload
from app.api.routes.clients_v3.models.onboarding_sections import IdentitySection
from app.domain.client_constants import INDUSTRIES, REGIONS


# ── Fake supabase (patrón test_insert_client_aria) ──
class _Q:
    def __init__(self, store: dict, table: str) -> None:
        self.store = store
        self.table_name = table

    def update(self, fields: dict) -> "_Q":
        self.store["updates"].append((self.table_name, dict(fields)))
        return self

    def eq(self, col: str, val: object) -> "_Q":
        self.store["eq"].append((col, val))
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=[{"client_id": "c-new"}])


class _Client:
    def __init__(self, store: dict) -> None:
        self.store = store

    def table(self, name: str) -> _Q:
        return _Q(self.store, name)


def _patch_repo(monkeypatch: pytest.MonkeyPatch, owner_ids: set) -> dict:
    store: dict = {"updates": [], "eq": []}
    monkeypatch.setattr(repo, "_sb", lambda: _Client(store))
    monkeypatch.setattr(owners, "fetch_owner_user_ids", lambda: owner_ids)
    return store


def test_owner_business_born_enterprise_2099(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch_repo(monkeypatch, owner_ids={"u-owner"})
    assert repo.promote_if_owner("u-owner", "c-new") is True
    assert store["updates"] == [("client_plans",
        {"plan": "enterprise", "current_period_end": "2099-12-31T00:00:00+00:00"})]
    assert ("client_id", "c-new") in store["eq"]   # promueve SOLO el negocio nuevo


def test_normal_account_no_change(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch_repo(monkeypatch, owner_ids={"u-someone-else"})
    assert repo.promote_if_owner("u-normal", "c-new") is False
    assert store["updates"] == []                  # default/trial intacto · cero writes


def test_isolation_only_plan_never_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch_repo(monkeypatch, owner_ids={"u-owner"})
    repo.promote_if_owner("u-owner", "c-new")
    assert {t for t, _ in store["updates"]} == {"client_plans"}  # NUNCA toca clients


def test_handler_wires_owner_enterprise(monkeypatch: pytest.MonkeyPatch) -> None:
    """El handler llama promote_if_owner con (user_id, client_id) en ese orden (anti-swap)."""
    calls: list = []

    async def _fake_user(auth: object) -> dict:
        return {"id": "u-owner", "role": "client"}

    async def _fake_safe(label: str, fn: object, *a: object, **k: object) -> None:
        calls.append((label, fn, a))
        return None

    monkeypatch.setattr(handler, "get_current_user", _fake_user)
    monkeypatch.setattr(repo, "resolve_owned_reseller_id", lambda uid: "r1")
    monkeypatch.setattr(repo, "insert_client", lambda *a, **k: "c-new")
    monkeypatch.setattr(repo, "upsert_client_context", lambda *a, **k: None)
    monkeypatch.setattr(repo, "bulk_insert_social_accounts", lambda *a, **k: None)
    monkeypatch.setattr(repo, "insert_brand_voice_samples", lambda *a, **k: None)
    monkeypatch.setattr(repo, "safe_insert", _fake_safe)

    payload = OnboardingPayload(identity=IdentitySection(
        name="Biz", industry=next(iter(INDUSTRIES)), regions=[next(iter(REGIONS))]))
    resp = asyncio.run(handler.create_client_onboarding(payload, authorization="x"))
    assert resp.client_id == "c-new"
    owner = [c for c in calls if c[0] == "owner_enterprise"]
    assert owner == [("owner_enterprise", repo.promote_if_owner, ("u-owner", "c-new"))]
