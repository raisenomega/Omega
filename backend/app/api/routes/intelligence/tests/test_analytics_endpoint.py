"""/intelligence/analytics · AISLAMIENTO per-negocio + honestidad (el riesgo #1 con 1 key · 11 cuentas).

CRÍTICO: con UNA key de Zernio que ve 11 cuentas, el negocio activo NO debe ver datos de otro.
- repo: get_zernio_accounts(client_id) filtra por client_id → nunca trae cuentas de otro negocio.
- handler: client_id ajeno → resolve_client_or_403 levanta 403 (Mail Boxes no puede pedir como Raisen).
- handler: scopea por el profileId/cuentas DEL negocio pedido · sin profile/cuentas → empty honesto (no ceros).
"""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

arepo = importlib.import_module("app.api.routes.intelligence._analytics_repository")
h = importlib.import_module("app.api.routes.intelligence.handlers.analytics_social")


class _Q:
    def __init__(self, rows): self.rows, self._eqs, self._nn = rows, {}, None
    def select(self, *a, **k): return self
    def eq(self, c, v): self._eqs[c] = v; return self
    @property
    def not_(self): return self
    def is_(self, c, v): self._nn = c if v == "null" else self._nn; return self
    def limit(self, n): return self
    def execute(self):
        out = [r for r in self.rows if all(r.get(k) == v for k, v in self._eqs.items())]
        if self._nn: out = [r for r in out if r.get(self._nn) is not None]
        return SimpleNamespace(data=out)


def test_get_accounts_filtra_por_negocio(monkeypatch):
    # Mail Boxes (IG+FB) y Raisen (IG) conviven bajo la misma key → cada uno ve SOLO lo suyo.
    rows = [{"client_id": "mailbox", "platform": "instagram", "zernio_account_id": "ig_mb"},
            {"client_id": "mailbox", "platform": "facebook", "zernio_account_id": "fb_mb"},
            {"client_id": "raisen", "platform": "instagram", "zernio_account_id": "ig_raisen"}]
    monkeypatch.setattr(arepo, "_sb", lambda: SimpleNamespace(table=lambda t: _Q(rows)))
    assert {a["account_id"] for a in arepo.get_zernio_accounts("mailbox")} == {"ig_mb", "fb_mb"}  # NO ig_raisen
    assert arepo.get_zernio_accounts("raisen") == [{"platform": "instagram", "account_id": "ig_raisen"}]


def test_accounts_ignora_binding_null(monkeypatch):
    rows = [{"client_id": "mailbox", "platform": "tiktok", "zernio_account_id": None}]
    monkeypatch.setattr(arepo, "_sb", lambda: SimpleNamespace(table=lambda t: _Q(rows)))
    assert arepo.get_zernio_accounts("mailbox") == []


def _auth(monkeypatch):
    async def _gcu(_a): return {"id": "u1"}
    monkeypatch.setattr(h, "get_current_user", _gcu)


def test_client_id_ajeno_da_403(monkeypatch):
    # Mail Boxes pidiendo con el client_id de Raisen → 403 (resolve_client_or_403 lo rechaza).
    _auth(monkeypatch)
    def _r(uid, cid): raise HTTPException(status_code=403, detail="forbidden_client")
    monkeypatch.setattr(h, "resolve_client_or_403", _r)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(h.social_analytics(authorization="Bearer x", client_id="raisen"))
    assert ei.value.status_code == 403


def test_sin_profile_ni_cuentas_empty_honesto(monkeypatch):
    # negocio sin Zernio → connected=False + message · CERO números (no finge datos).
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "mailbox"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: None)
    monkeypatch.setattr(h.arepo, "get_zernio_accounts", lambda cid: [])
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="mailbox"))
    assert out.connected is False and out.message
    assert out.total_followers is None and out.avg_engagement is None and out.posts == 0
    assert out.growth == [] and out.engagement == [] and out.heatmap == []


def test_ensambla_solo_datos_del_negocio_pedido(monkeypatch):
    # Scope correcto: usa el profileId/cuenta DEL negocio · arma el shape real de Zernio.
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "mailbox"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: "prof_mb")
    monkeypatch.setattr(h.arepo, "get_zernio_accounts",
                        lambda cid: [{"platform": "instagram", "account_id": "ig_mb"}])
    seen = {}
    async def _daily(pid): seen["daily"] = pid; return {"dailyData": [{"postCount": 2, "metrics": {
        "likes": 8, "comments": 2, "shares": 0, "impressions": 100},
        "platformMetrics": {"instagram": {"likes": 8, "comments": 2, "shares": 0}}}]}
    async def _best(pid): return {"slots": []}
    async def _fh(aid): seen["fh"] = aid; return {"metrics": {"follower_count": {
        "total": 500, "values": [{"date": "2026-06-19", "value": 500}]}}}
    monkeypatch.setattr(h.za, "daily_metrics", _daily)
    monkeypatch.setattr(h.za, "best_time", _best)
    monkeypatch.setattr(h.za, "follower_history", _fh)
    h._cache.clear()
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="mailbox"))
    assert seen == {"daily": "prof_mb", "fh": "ig_mb"}  # scope = el negocio pedido, no otro
    assert out.connected and out.total_followers == 500 and out.posts == 2 and out.avg_engagement == 10.0
    assert [g.model_dump() for g in out.growth] == [{"date": "2026-06-19", "followers": 500}]
    assert out.data_delay
