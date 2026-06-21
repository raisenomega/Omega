"""_analytics_assembler · ensamblado PURO con el SHAPE REAL de la sonda (resolución por profileId).

AISLAMIENTO por profileId (la llave canónica): el fixture mezcla cuentas de DOS profiles + page_follows=26
presente. El total de un negocio = Σ followersCount de SUS cuentas (por profileId), NUNCA 28, NUNCA suma
el otro profile. Anti "solo uno funciona": ambos profiles resuelven. SIN KPI Posts (removido · opción 3).
"""
from app.api.routes.intelligence import _analytics_assembler as asm

# /accounts REAL: profileId como string Y como objeto {_id,name} (Zernio da ambas formas) · page_follows trampa.
_ACCOUNTS = [
    {"_id": "ig_mb", "platform": "instagram", "profileId": "prof_mb",
     "followersCount": 2, "externalPostCount": 3, "page_follows": {"total": 26}},
    {"_id": "fb_mb", "platform": "facebook", "profileId": {"_id": "prof_mb", "name": "Mail Boxes"},
     "followersCount": 3, "page_follows": {"total": 26}},
    {"_id": "tt_mb", "platform": "tiktok", "profileId": "prof_mb", "followersCount": 0},
    {"_id": "ig_or", "platform": "instagram", "profileId": "prof_or", "followersCount": 3},  # OTRO negocio
    {"_id": "fb_or", "platform": "facebook", "profileId": "prof_or", "followersCount": 2},
]
_BEST = {"slots": [{"day_of_week": 1, "hour": 19, "avg_engagement": 42.0},
                   {"day_of_week": 3, "hour": 12, "avg_engagement": 8.5}]}
_DAILY = {"dailyData": [
    {"platformMetrics": {"instagram": {"likes": 6, "comments": 3, "shares": 1, "saves": 2, "views": 100},
                         "facebook": {"likes": 4, "comments": 1, "shares": 0, "saves": 0, "views": 40}}},
    {"platformMetrics": {"instagram": {"likes": 5, "comments": 0, "shares": 0, "saves": 1, "views": 80}}}]}


def test_followers_por_profileid_es_5_nunca_28():
    total = asm.followers_total(_ACCOUNTS, "prof_mb")
    assert total == 5            # 2 (IG) + 3 (FB · profileId objeto) + 0 (TikTok)
    assert total != 28           # regresión: jamás la suma de page_follows


def test_followers_aislado_no_suma_otro_profile():
    # prof_or (3+2=5) NO se suma a prof_mb, y prof_mb (5) no se suma a prof_or → anti "solo uno funciona".
    assert asm.followers_total(_ACCOUNTS, "prof_mb") == 5
    assert asm.followers_total(_ACCOUNTS, "prof_or") == 5   # el OTRO negocio también resuelve, aislado


def test_followers_none_si_profile_sin_cuentas():
    assert asm.followers_total(_ACCOUNTS, "prof_fantasma") is None   # None, NO 0 (no finge "0 seguidores")
    assert asm.followers_total([], "prof_mb") is None


def test_ig_account_ids_por_profile():
    assert asm.ig_account_ids(_ACCOUNTS, "prof_mb") == ["ig_mb"]     # solo IG del profile (no fb/tt, no otro profile)
    assert asm.ig_account_ids(_ACCOUNTS, "prof_or") == ["ig_or"]


def test_sin_kpi_posts():
    # opción 3: el assembler ya no expone posts_total (la API no da ventana 'this period').
    assert not hasattr(asm, "posts_total")


def test_best_hour_derivado_no_hardcode():
    assert asm.best_hour(_BEST) == "19:00"           # slot de mayor avg_engagement (42.0), NO string fijo
    assert asm.best_hour({}) is None                 # sin slots → None honesto


def test_engagement_por_red_con_saves_views_sin_pct():
    rows = {r["platform"]: r for r in asm.engagement_by_network(_DAILY)}
    assert rows["instagram"] == {"platform": "instagram", "likes": 11, "comments": 3,
                                 "shares": 1, "saves": 3, "views": 180}
    assert rows["facebook"]["views"] == 40
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
    assert asm.best_hour({}) is None
