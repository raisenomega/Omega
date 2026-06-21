"""Fase B · derive_bindings_from_profile = LA rutina raíz (onboarding + backfill · MISMA función).

Atrapa el bug que motivó el fix: un negocio con profile pero SIN bindings → tras la rutina, TODAS sus
cuentas quedan bindeadas (no puede nacer roto). Idempotente (2x = mismas filas). Aislado por profileId
(una cuenta de otro profile NO se bindea). B==C: la misma función produce el mismo resultado. G9 exime tests."""
import asyncio
from types import SimpleNamespace

import app.api.routes.clients_v3.handlers._zernio_persist as p

# /accounts del workspace: 3 del profile del negocio (prof_mb) + 1 de OTRO profile (no debe bindearse).
_ACCOUNTS = [
    {"_id": "ig_mb", "platform": "instagram", "profileId": "prof_mb", "username": "@mb_ig"},
    {"_id": "fb_mb", "platform": "facebook", "profileId": {"_id": "prof_mb", "name": "MB"}, "displayName": "MB FB"},
    {"_id": "tt_mb", "platform": "tiktok", "profileId": "prof_mb", "username": "@mb_tt"},
    {"_id": "ig_other", "platform": "instagram", "profileId": "prof_other", "username": "@otro"},
]


class _FakeTable:
    def __init__(self, store):
        self.store, self._eqs, self._op, self._payload = store, {}, None, None
    def select(self, *a): self._op = "select"; return self
    def insert(self, payload): self._op, self._payload = "insert", payload; return self
    def update(self, payload): self._op, self._payload = "update", payload; return self
    def eq(self, c, v): self._eqs[c] = v; return self
    def limit(self, n): return self
    def execute(self):
        if self._op == "select":
            return SimpleNamespace(data=[r for r in self.store
                                         if all(r.get(k) == v for k, v in self._eqs.items())])
        if self._op == "insert":
            self.store.append({**self._payload, "id": f"id{len(self.store)}"})
            return SimpleNamespace(data=[self.store[-1]])
        for r in self.store:                                     # update
            if all(r.get(k) == v for k, v in self._eqs.items()):
                r.update(self._payload)
        return SimpleNamespace(data=[])


def _wire(monkeypatch, store, accounts=_ACCOUNTS):
    async def _accs(profile_id): return accounts
    monkeypatch.setattr(p, "list_accounts", _accs)
    monkeypatch.setattr(p, "get_supabase_service",
                        lambda: SimpleNamespace(client=SimpleNamespace(table=lambda n: _FakeTable(store))))


def test_nace_roto_atrapado(monkeypatch):
    # negocio con profile pero 0 bindings → derive → TODAS sus cuentas del profile quedan bindeadas.
    store: list = []
    _wire(monkeypatch, store)
    written = asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    plats = {r["platform"] for r in store}
    assert plats == {"instagram", "facebook", "tiktok"}        # las 3 del profile · NINGUNA vacía
    assert {r["zernio_account_id"] for r in store} == {"ig_mb", "fb_mb", "tt_mb"}
    assert len(written) == 3 and all(r["oauth_status"] == "connected" for r in store)


def test_aislamiento_no_bindea_otro_profile(monkeypatch):
    # ig_other (prof_other) está en /accounts pero NO es del profile → no se bindea (anti "solo uno funciona").
    store: list = []
    _wire(monkeypatch, store)
    asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    assert "ig_other" not in {r["zernio_account_id"] for r in store}
    assert "@otro" not in {r.get("zernio_account_handle") for r in store}


def test_idempotente_2x_sin_duplicar(monkeypatch):
    # correr la rutina 2 veces = mismas filas (la 2da actualiza, no inserta). Prueba de raíz: no ensucia.
    store: list = []
    _wire(monkeypatch, store)
    asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    assert len(store) == 3                                      # 3, NO 6 · cero duplicados
    assert {r["platform"] for r in store} == {"instagram", "facebook", "tiktok"}


def test_handle_autoritativo_de_zernio(monkeypatch):
    # el handle sale de username/displayName de Zernio (no de inputs) · _upsert_binding compartido.
    store: list = []
    _wire(monkeypatch, store)
    asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    by_plat = {r["platform"]: r for r in store}
    assert by_plat["instagram"]["zernio_account_handle"] == "@mb_ig"
    assert by_plat["facebook"]["zernio_account_handle"] == "MB FB"   # displayName cuando no hay username


def test_b_igual_c_mismo_resultado(monkeypatch):
    # B (onboarding) y C (backfill) son la MISMA función → mismo set de bindings sobre el mismo profile.
    store_b: list = []
    _wire(monkeypatch, store_b)
    asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    store_c: list = []
    _wire(monkeypatch, store_c)
    asyncio.run(p.derive_bindings_from_profile("mailbox", "prof_mb"))
    key = lambda s: sorted((r["platform"], r["zernio_account_id"]) for r in s)
    assert key(store_b) == key(store_c)                        # onboarding == backfill
