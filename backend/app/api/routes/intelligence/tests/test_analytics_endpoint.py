"""/intelligence/analytics · AISLAMIENTO per-negocio + honestidad (el riesgo con 1 key · 11 cuentas).

CRÍTICO: el negocio activo NO ve datos de otro. followers/posts se suman SOLO de las cuentas vinculadas
(bound_ids). client_id ajeno → 403. Sin profile/cuentas → empty honesto (NO ceros). ANTI-28 e2e:
/accounts trae page_follows=26 presente pero el total da 5 (Σ followersCount de Mail Boxes), nunca 28.
"""
import asyncio
import importlib

import pytest
from fastapi import HTTPException

h = importlib.import_module("app.api.routes.intelligence.handlers.analytics_social")

_ACCOUNTS_API = [
    {"_id": "ig_mb", "followersCount": 2, "externalPostCount": 3, "page_follows": {"total": 26}},
    {"_id": "fb_mb", "followersCount": 3, "externalPostCount": 1, "page_follows": {"total": 26}},
    {"_id": "tt_mb", "followersCount": 0, "externalPostCount": 1},
    {"_id": "ig_raisen", "followersCount": 999, "externalPostCount": 50},  # OTRO negocio · no debe sumar
]


def _auth(monkeypatch):
    async def _gcu(_a): return {"id": "u1"}
    monkeypatch.setattr(h, "get_current_user", _gcu)


def test_client_id_ajeno_da_403(monkeypatch):
    _auth(monkeypatch)
    def _r(uid, cid): raise HTTPException(status_code=403, detail="forbidden_client")
    monkeypatch.setattr(h, "resolve_client_or_403", _r)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(h.social_analytics(authorization="Bearer x", client_id="raisen"))
    assert ei.value.status_code == 403


def test_sin_profile_ni_cuentas_empty_honesto(monkeypatch):
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "mailbox"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: None)
    monkeypatch.setattr(h.arepo, "get_zernio_accounts", lambda cid: [])
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="mailbox"))
    assert out.connected is False and out.message
    assert out.total_followers is None and out.posts == 0 and out.best_hour is None
    assert out.growth == [] and out.engagement == [] and out.heatmap == []


def test_ensambla_aislado_total_5_nunca_28(monkeypatch):
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "mailbox"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: "prof_mb")
    monkeypatch.setattr(h.arepo, "get_zernio_accounts", lambda cid: [
        {"platform": "instagram", "account_id": "ig_mb"},
        {"platform": "facebook", "account_id": "fb_mb"},
        {"platform": "tiktok", "account_id": "tt_mb"}])
    seen = {}
    async def _accs(): return _ACCOUNTS_API
    async def _daily(pid): seen["daily"] = pid; return {"dailyData": [{"platformMetrics": {
        "instagram": {"likes": 8, "comments": 2, "shares": 0, "saves": 1, "views": 100}}}]}
    async def _best(pid): return {"slots": [{"day_of_week": 1, "hour": 19, "avg_engagement": 40.0}]}
    async def _fh(aid): seen["fh"] = aid; return {"metrics": {"follower_count": {
        "total": 2, "values": [{"date": "2026-06-21", "value": 2}]}}}
    monkeypatch.setattr(h.za, "list_accounts", _accs)
    monkeypatch.setattr(h.za, "daily_metrics", _daily)
    monkeypatch.setattr(h.za, "best_time", _best)
    monkeypatch.setattr(h.za, "follower_history", _fh)
    h._cache.clear()
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="mailbox"))
    assert seen == {"daily": "prof_mb", "fh": "ig_mb"}      # scope = el negocio pedido
    assert out.connected is True
    assert out.total_followers == 5 and out.total_followers != 28   # NUNCA 28 · ig_raisen(999) excluido
    assert out.posts == 5                                    # externalPostCount 3+1+1
    assert out.best_hour == "19:00"                          # derivado, no hardcode
    assert [g.model_dump() for g in out.growth] == [{"date": "2026-06-21", "followers": 2}]
    # sin porcentaje en ninguna parte de la respuesta
    assert not hasattr(out, "avg_engagement")
    assert out.engagement[0].model_dump() == {"platform": "instagram", "likes": 8, "comments": 2,
                                              "shares": 0, "saves": 1, "views": 100}
    assert out.data_delay
