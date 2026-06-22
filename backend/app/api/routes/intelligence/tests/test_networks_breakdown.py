"""Chip per-red · networks_breakdown AISLADO por profileId. Valores REALES de la sonda (MB):
ig followers2/reach155/ER5.8 · fb followers3/reach0/ER— (None, no 0 disfrazado) · cuenta de OTRO
negocio (prof_or) NO se cuela. Mismo blindaje profileId de todo el arco."""
from app.api.routes.intelligence import _analytics_metrics as met

# cuentas del workspace: 3 de MB (prof_mb) + 1 de OR (prof_or · para probar aislamiento)
ACCOUNTS = [
    {"_id": "ig_mb", "platform": "instagram", "profileId": "prof_mb", "followersCount": 2},
    {"_id": "fb_mb", "platform": "facebook", "profileId": "prof_mb", "followersCount": 3},
    {"_id": "tt_mb", "platform": "tiktok", "profileId": "prof_mb", "followersCount": 0},
    {"_id": "ig_or", "platform": "instagram", "profileId": "prof_or", "followersCount": 99},  # ajeno
]
MB_DAILY = {
    "platformBreakdown": [
        {"platform": "instagram", "reach": 155, "likes": 7, "comments": 0, "shares": 1, "saves": 1, "views": 251},
        {"platform": "facebook", "reach": 0, "likes": 0, "comments": 0, "shares": 0, "saves": 0, "views": 86},
        {"platform": "tiktok", "reach": 0, "likes": 0, "comments": 0, "shares": 0, "saves": 0, "views": 0},
    ],
    "dailyData": [
        {"date": "2026-06-20", "platformMetrics": {"instagram": {"impressions": 251, "reach": 155, "likes": 7, "comments": 0, "shares": 1, "saves": 1, "clicks": 0, "views": 251, "postCount": 5}}},
        {"date": "2026-04-11", "platformMetrics": {"facebook": {"impressions": 86, "reach": 0, "likes": 0, "comments": 0, "shares": 0, "saves": 0, "clicks": 0, "views": 86, "postCount": 1}}},
    ],
}


def _by_net(daily=MB_DAILY, accounts=ACCOUNTS, pid="prof_mb"):
    return {n["platform"]: n for n in met.networks_breakdown(daily, accounts, pid)}


def test_networks_solo_las_del_profile_aisladas():
    nets = _by_net()
    assert set(nets) == {"instagram", "facebook", "tiktok"}   # las 3 de MB · NO la de prof_or


def test_instagram_valores_reales():
    ig = _by_net()["instagram"]
    assert ig["followers"] == 2 and ig["reach"] == 155
    assert ig["profile_engagement"] == 5.8                    # 9/155*100 (de ESA red)
    assert ig["likes"] == 7 and ig["views"] == 251
    assert [p["date"] for p in ig["engagement_series"]] == ["2026-06-20"]
    assert ig["posts_series"] == [{"date": "2026-06-20", "count": 5}]


def test_facebook_reach_cero_ER_none_no_disfrazado():
    """reach=0 → ER None (—), NUNCA 0% · distinción 0-real-vs-ausente del arco."""
    fb = _by_net()["facebook"]
    assert fb["followers"] == 3 and fb["reach"] == 0
    assert fb["profile_engagement"] is None                   # '—' honesto, no 0%
    assert fb["views"] == 86


def test_followers_aislados_no_cruzan_negocios():
    """El followers de IG es el de MB (2), JAMÁS el de la cuenta IG ajena (prof_or=99)."""
    assert _by_net()["instagram"]["followers"] == 2
    assert all(n["followers"] != 99 for n in met.networks_breakdown(MB_DAILY, ACCOUNTS, "prof_mb"))


def test_red_sin_platformMetrics_series_vacias():
    """tiktok no tiene platformMetrics en dailyData → series [] (empty honesto, no inventa)."""
    tt = _by_net()["tiktok"]
    assert tt["engagement_series"] == [] and tt["posts_series"] == []
    assert tt["profile_engagement"] is None                   # reach 0 → —
