"""/intelligence/analytics · AISLAMIENTO por profileId (la llave canónica · el riesgo con 1 key · 11 cuentas).

El negocio activo resuelve por SU profileId; followers/serie salen de Zernio filtrado por ese profileId
(NO bound_ids). client_id ajeno → 403. Sin profileId (Milagrosa) → empty honesto. Anti "solo uno funciona":
el mismo /accounts mezcla dos profiles y cada negocio ve SOLO el suyo. SIN KPI Posts (opción 3). ANTI-28.
"""
import asyncio
import importlib

import pytest
from fastapi import HTTPException

h = importlib.import_module("app.api.routes.intelligence.handlers.analytics_social")

# /accounts (todo el workspace · 2 profiles + page_follows trampa). El handler filtra por profileId.
_ACCOUNTS_API = [
    {"_id": "ig_mb", "platform": "instagram", "profileId": "prof_mb", "followersCount": 2,
     "page_follows": {"total": 26}},
    {"_id": "fb_mb", "platform": "facebook", "profileId": "prof_mb", "followersCount": 3},
    {"_id": "tt_mb", "platform": "tiktok", "profileId": "prof_mb", "followersCount": 0},
    {"_id": "ig_or", "platform": "instagram", "profileId": "prof_or", "followersCount": 99},  # OTRO negocio
]


def _auth(monkeypatch):
    async def _gcu(_a): return {"id": "u1"}
    monkeypatch.setattr(h, "get_current_user", _gcu)


def _wire_zernio(monkeypatch, seen):
    async def _accs(): return _ACCOUNTS_API
    async def _daily(pid): seen["daily"] = pid; return {"dailyData": [{"date": "2026-06-21", "postCount": 3, "metrics": {"reach": 100, "likes": 8, "comments": 2, "shares": 0, "saves": 1, "views": 100, "impressions": 100, "clicks": 0}, "platformMetrics": {
        "instagram": {"likes": 8, "comments": 2, "shares": 0, "saves": 1, "views": 100, "reach": 100}}}]}
    async def _best(pid): return {"slots": [{"day_of_week": 1, "hour": 19, "avg_engagement": 40.0}]}
    async def _fh(aid): seen.setdefault("fh", []).append(aid); return {"metrics": {"follower_count": {
        "total": 2, "values": [{"date": "2026-06-21", "value": 2}]}}}
    monkeypatch.setattr(h.za, "list_accounts", _accs)
    monkeypatch.setattr(h.za, "daily_metrics", _daily)
    monkeypatch.setattr(h.za, "best_time", _best)
    monkeypatch.setattr(h.za, "follower_history", _fh)
    h._cache.clear()


def test_client_id_ajeno_da_403(monkeypatch):
    _auth(monkeypatch)
    def _r(uid, cid): raise HTTPException(status_code=403, detail="forbidden_client")
    monkeypatch.setattr(h, "resolve_client_or_403", _r)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(h.social_analytics(authorization="Bearer x", client_id="ajeno"))
    assert ei.value.status_code == 403


def test_sin_profile_empty_honesto(monkeypatch):
    # Milagrosa: sin zernio_profile_id → connected=False + message · CERO números (no finge datos).
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "milagrosa"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: None)
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="milagrosa"))
    assert out.connected is False and out.message
    assert out.total_followers is None and out.best_hour is None
    assert out.growth == [] and out.engagement == [] and out.heatmap == []
    assert not hasattr(out, "posts")             # KPI Posts removido (opción 3)


def test_resuelve_por_profileid_aislado(monkeypatch):
    # Mail Boxes (prof_mb): followers=5 por profileId · NUNCA 28 · NUNCA suma ig_or (99) del otro profile.
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "mailbox"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: "prof_mb")
    seen: dict = {}
    _wire_zernio(monkeypatch, seen)
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="mailbox"))
    assert seen == {"daily": "prof_mb", "fh": ["ig_mb"]}        # scope por profileId · solo IG del profile
    assert out.connected is True
    assert out.total_followers == 5 and out.total_followers != 28   # 2+3+0 · ig_or(99) excluido
    assert out.best_hour == "19:00"
    assert [g.model_dump() for g in out.growth] == [{"date": "2026-06-21", "followers": 2}]
    assert not hasattr(out, "posts")             # sin KPI Posts
    assert out.engagement[0].model_dump() == {"platform": "instagram", "likes": 8, "comments": 2,
                                              "shares": 0, "saves": 1, "views": 100, "reach": 100}
    # panel ampliado wired: total_reach + ER histórico + series (acumulado · derivado de la misma data)
    assert out.total_reach == 100
    assert out.profile_engagement == 11.0                       # (8+2+0+1)/100*100
    assert [p.model_dump() for p in out.posts_series] == [{"date": "2026-06-21", "count": 3}]
    assert out.engagement_series[0].model_dump()["reach"] == 100
    assert not hasattr(out, "data_delay")        # delay removido (proveedor invisible · Commit 3)


def test_anti_solo_uno_funciona(monkeypatch):
    # El OTRO negocio (prof_or) también resuelve por profileId, aislado → ve SUS 99, no los de Mail Boxes.
    _auth(monkeypatch)
    monkeypatch.setattr(h, "resolve_client_or_403", lambda uid, cid: {"id": "otro"})
    monkeypatch.setattr(h.arepo, "get_zernio_profile_id", lambda cid: "prof_or")
    _wire_zernio(monkeypatch, {})
    out = asyncio.run(h.social_analytics(authorization="Bearer x", client_id="otro"))
    assert out.connected is True and out.total_followers == 99    # SUS datos, no los de prof_mb (5)
