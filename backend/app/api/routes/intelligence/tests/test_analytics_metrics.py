"""Panel ampliado · métricas ACUMULADO. Fixtures = valores REALES de la sonda (21 jun · MB+OR).
NO inventados (lección del 28: el test cuadra contra la realidad). Verifica AMBOS negocios y que
no se cruzan. ER con label histórico vive en el modelo · '—' (None) honesto si reach=0."""
from app.api.routes.intelligence import _analytics_assembler as asm
from app.api.routes.intelligence import _analytics_metrics as met

# --- shape REAL de daily-metrics (sonda) · MB: reach155, inter9 → ER 5.8% · 5 posts+2 ---
MB_DAILY = {
    "dailyData": [
        {"date": "2026-06-20", "postCount": 5,
         "metrics": {"impressions": 251, "reach": 155, "likes": 7, "comments": 0, "shares": 1, "saves": 1, "clicks": 0, "views": 251},
         "platformMetrics": {"instagram": {"likes": 7, "comments": 0, "shares": 1, "saves": 1, "views": 251, "reach": 155}}},
        {"date": "2026-04-11", "postCount": 2,
         "metrics": {"impressions": 86, "reach": 0, "likes": 0, "comments": 0, "shares": 0, "saves": 0, "clicks": 0, "views": 86},
         "platformMetrics": {"facebook": {"likes": 0, "comments": 0, "shares": 0, "saves": 0, "views": 86, "reach": 0}}},
    ],
}
# OR: reach11, inter2 → ER 18.2% · 3+1 posts
OR_DAILY = {
    "dailyData": [
        {"date": "2026-06-08", "postCount": 3,
         "metrics": {"impressions": 25, "reach": 11, "likes": 2, "comments": 0, "shares": 0, "saves": 0, "clicks": 0, "views": 25},
         "platformMetrics": {"instagram": {"likes": 2, "comments": 0, "shares": 0, "saves": 0, "views": 25, "reach": 11}}},
        {"date": "2026-05-29", "postCount": 1,
         "metrics": {"impressions": 0, "reach": 0, "likes": 0, "comments": 0, "shares": 0, "saves": 0, "clicks": 0, "views": 0},
         "platformMetrics": {"facebook": {"likes": 0, "comments": 0, "shares": 0, "saves": 0, "views": 0, "reach": 0}}},
    ],
}


def test_engagement_by_network_incluye_reach():
    rows = {r["platform"]: r for r in asm.engagement_by_network(MB_DAILY)}
    assert rows["instagram"]["reach"] == 155 and rows["instagram"]["likes"] == 7
    assert rows["facebook"]["views"] == 86 and rows["facebook"]["reach"] == 0


def test_total_reach_y_ER_MB_reales():
    rows = asm.engagement_by_network(MB_DAILY)
    assert met.total_reach(rows) == 155                 # sonda MB
    assert met.profile_engagement(rows) == 5.8          # 9/155*100 → 5.8 (histórico)


def test_total_reach_y_ER_OR_reales():
    rows = asm.engagement_by_network(OR_DAILY)
    assert met.total_reach(rows) == 11                  # sonda OR
    assert met.profile_engagement(rows) == 18.2         # 2/11*100 → 18.2 (reach chico · por eso 'histórico')


def test_aislamiento_MB_vs_OR_no_se_cruzan():
    """Cada negocio da SUS números (no 'cuadró en uno'): MB≠OR en reach y ER."""
    mb, orr = asm.engagement_by_network(MB_DAILY), asm.engagement_by_network(OR_DAILY)
    assert met.total_reach(mb) == 155 and met.total_reach(orr) == 11
    assert met.profile_engagement(mb) == 5.8 and met.profile_engagement(orr) == 18.2


def test_ER_reach_cero_es_none_honesto():
    """reach=0 → None (UI '—', NUNCA 0 ni div/0 ni % engañoso)."""
    zero = {"dailyData": [{"date": "2026-06-01", "postCount": 1,
            "metrics": {}, "platformMetrics": {"facebook": {"likes": 5, "reach": 0}}}]}
    rows = asm.engagement_by_network(zero)
    assert met.total_reach(rows) is not None            # hay filas → reach total = 0 (real)
    assert met.profile_engagement(rows) is None         # pero ER con reach=0 → '—' honesto


def test_total_reach_sin_filas_es_none():
    assert met.total_reach([]) is None                  # sin datos → '—', no 0


def test_engagement_series_8_campos_ordenada():
    s = met.engagement_series(MB_DAILY)
    assert [p["date"] for p in s] == ["2026-04-11", "2026-06-20"]   # ordenada por fecha
    last = s[-1]
    for k in ("impressions", "reach", "likes", "comments", "shares", "saves", "clicks", "views"):
        assert k in last                                # 8 campos
    assert last["reach"] == 155 and last["views"] == 251


def test_posts_series_por_dia_acumulado():
    p = met.posts_series(MB_DAILY)
    assert p == [{"date": "2026-04-11", "count": 2}, {"date": "2026-06-20", "count": 5}]
    assert met.posts_series(OR_DAILY) == [{"date": "2026-05-29", "count": 1}, {"date": "2026-06-08", "count": 3}]


def test_series_descartan_dia_sin_fecha():
    d = {"dailyData": [{"postCount": 9, "metrics": {"reach": 1}}, {"date": "2026-06-01", "postCount": 2, "metrics": {}}]}
    assert len(met.engagement_series(d)) == 1 and len(met.posts_series(d)) == 1   # el sin-fecha se descarta


def test_empty_daily_series_vacias():
    assert met.engagement_series({}) == [] and met.posts_series({}) == []   # empty honesto
