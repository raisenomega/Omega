"""_analytics_assembler · ensamblado PURO con el SHAPE REAL de la sonda (la lección del 28).

ANTI-28: el fixture trae /accounts con followersCount 2/3/0 Y page_follows.total=26 presente.
El total DEBE = Σ followersCount filtrado por bound_ids = 5, NUNCA 28, y el código jamás toca page_follows.
Cero porcentajes · entrada vacía → salida vacía honesta.
"""
from app.api.routes.intelligence import _analytics_assembler as asm

# /accounts REAL: followersCount (snapshot) + externalPostCount + page_follows presente (trampa del 28).
_ACCOUNTS = [
    {"_id": "ig_mb", "platform": "instagram", "followersCount": 2, "externalPostCount": 3,
     "page_follows": {"total": 26}},  # ← presente a propósito · NUNCA debe usarse
    {"_id": "fb_mb", "platform": "facebook", "followersCount": 3, "externalPostCount": 1,
     "page_follows": {"total": 26}},
    {"_id": "tt_mb", "platform": "tiktok", "followersCount": 0, "externalPostCount": 1},
    {"_id": "ig_raisen", "platform": "instagram", "followersCount": 999, "externalPostCount": 50},  # OTRO negocio
]
_BOUND = ["ig_mb", "fb_mb", "tt_mb"]  # solo Mail Boxes
_BEST = {"slots": [{"day_of_week": 1, "hour": 19, "avg_engagement": 42.0},
                   {"day_of_week": 3, "hour": 12, "avg_engagement": 8.5}]}
_DAILY = {"dailyData": [
    {"platformMetrics": {"instagram": {"likes": 6, "comments": 3, "shares": 1, "saves": 2, "views": 100},
                         "facebook": {"likes": 4, "comments": 1, "shares": 0, "saves": 0, "views": 40}}},
    {"platformMetrics": {"instagram": {"likes": 5, "comments": 0, "shares": 0, "saves": 1, "views": 80}}}]}


def test_followers_total_es_5_nunca_28():
    total = asm.followers_total(_ACCOUNTS, _BOUND)
    assert total == 5            # 2 (IG) + 3 (FB) + 0 (TikTok)
    assert total != 28           # regresión explícita: jamás la suma de page_follows


def test_followers_aislamiento_no_suma_otro_negocio():
    # ig_raisen (999) está en /accounts pero NO en bound_ids → no se suma.
    assert asm.followers_total(_ACCOUNTS, _BOUND) == 5
    assert asm.followers_total(_ACCOUNTS, ["ig_raisen"]) == 999  # ese negocio vería lo suyo, no Mail Boxes


def test_followers_none_si_ninguna_resuelve():
    assert asm.followers_total(_ACCOUNTS, ["fantasma"]) is None   # None, NO 0 (no finge "0 seguidores")
    assert asm.followers_total([], _BOUND) is None


def test_posts_total_real_no_interacciones():
    assert asm.posts_total(_ACCOUNTS, _BOUND) == 5   # 3 + 1 + 1 externalPostCount (NO Σ likes)


def test_best_hour_derivado_no_hardcode():
    assert asm.best_hour(_BEST) == "19:00"           # slot de mayor avg_engagement (42.0), NO string fijo
    assert asm.best_hour({}) is None                 # sin slots → None honesto


def test_engagement_por_red_con_saves_views_sin_pct():
    rows = {r["platform"]: r for r in asm.engagement_by_network(_DAILY)}
    assert rows["instagram"] == {"platform": "instagram", "likes": 11, "comments": 3,
                                 "shares": 1, "saves": 3, "views": 180}
    assert rows["facebook"]["views"] == 40
    # ninguna fila emite porcentaje
    assert all("rate" not in r and "engagement" not in r for r in rows.values())


def test_growth_serie_ig():
    hist = [{"metrics": {"follower_count": {"total": 2, "values": [
        {"date": "2026-06-20", "value": 2}, {"date": "2026-06-21", "value": 2}]}}}]
    assert asm.growth_series(hist) == [{"date": "2026-06-20", "followers": 2},
                                       {"date": "2026-06-21", "followers": 2}]


def test_vacio_no_inventa_nada():
    assert asm.engagement_by_network({}) == []
    assert asm.heatmap_cells({}) == []
    assert asm.growth_series([]) == []
    assert asm.posts_total([], _BOUND) == 0
    assert asm.best_hour({}) is None
