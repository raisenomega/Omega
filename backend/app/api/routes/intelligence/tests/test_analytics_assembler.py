"""_analytics_assembler · ensamblado PURO de Zernio → shape del panel (cero fabricación).

Verifica: con dato real arma growth/engagement/heatmap/KPIs · con {} vacío → salida vacía honesta
(None/[]/0), JAMÁS un número inventado (P1).
"""
from app.api.routes.intelligence import _analytics_assembler as asm

_DAILY = {
    "dailyData": [
        {"postCount": 2, "metrics": {"likes": 10, "comments": 4, "shares": 1, "impressions": 100},
         "platformMetrics": {"instagram": {"likes": 6, "comments": 3, "shares": 1},
                             "facebook": {"likes": 4, "comments": 1, "shares": 0}}},
        {"postCount": 3, "metrics": {"likes": 5, "comments": 0, "shares": 0, "impressions": 100},
         "platformMetrics": {"instagram": {"likes": 5, "comments": 0, "shares": 0}}},
    ]
}
_BEST = {"slots": [{"day_of_week": 1, "hour": 19, "avg_engagement": 42.0},
                   {"day_of_week": 3, "hour": 12, "avg_engagement": 8.5}]}
_IG_HIST = [{"metrics": {"follower_count": {"total": 1200, "values": [
    {"date": "2026-06-18", "value": 1180}, {"date": "2026-06-19", "value": 1200}]}}}]


def test_engagement_suma_por_plataforma():
    rows = asm.engagement_rows(_DAILY)
    by = {r["platform"]: r for r in rows}
    assert by["instagram"] == {"platform": "instagram", "likes": 11, "comments": 3, "shares": 1}
    assert by["facebook"] == {"platform": "facebook", "likes": 4, "comments": 1, "shares": 0}


def test_heatmap_mapea_slots():
    cells = asm.heatmap_cells(_BEST)
    assert {"day": "Lun", "hour": 19, "value": 42.0} in cells
    assert len(cells) == 2


def test_growth_serie_por_fecha_ordenada():
    series = asm.growth_series(_IG_HIST)
    assert series == [{"date": "2026-06-18", "followers": 1180}, {"date": "2026-06-19", "followers": 1200}]


def test_followers_total_suma_por_campo_de_plataforma():
    per = [("instagram", {"metrics": {"follower_count": {"total": 1200}}}),
           ("facebook", {"metrics": {"page_follows": {"total": 800}}})]
    assert asm.followers_total(per) == 2000


def test_avg_engagement_tasa_real():
    # (15+4+1)/200 *100 = 10.0
    assert asm.avg_engagement(_DAILY) == 10.0


def test_posts_suma_postcount():
    assert asm.posts_count(_DAILY) == 5


# --- HONESTIDAD: entrada vacía → salida vacía, NUNCA cero/numero inventado ---

def test_vacio_no_inventa_nada():
    assert asm.engagement_rows({}) == []
    assert asm.heatmap_cells({}) == []
    assert asm.growth_series([]) == []
    assert asm.followers_total([]) is None          # None, NO 0 (no finge "0 seguidores")
    assert asm.avg_engagement({}) is None            # None, NO 0.0% (no finge sin impresiones)
    assert asm.posts_count({}) == 0


def test_sin_total_no_cuenta_como_real():
    # cuenta cuyo insights vino vacío (sin "total") → no suma → None honesto si todas así.
    assert asm.followers_total([("tiktok", {"metrics": {}})]) is None
