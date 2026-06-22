"""Builder de social_metrics · EL test del arco (anti-fabricación: el 28 aplicado al almacén).
Datos reales de la sonda (MB). Real o None, NUNCA 0 fabricado · aislamiento por client_id."""
from app.workers._social_metrics_builder import build_snapshot_rows

# cuentas: 3 de MB (prof_mb) + 1 de OR (prof_or · para probar aislamiento)
ACCOUNTS = [
    {"_id": "ig", "platform": "instagram", "profileId": "prof_mb", "followersCount": 2},
    {"_id": "fb", "platform": "facebook", "profileId": "prof_mb", "followersCount": 3},
    {"_id": "tt", "platform": "tiktok", "profileId": "prof_mb", "followersCount": 0},
    {"_id": "ig_or", "platform": "instagram", "profileId": "prof_or", "followersCount": 99},
]
DAILY = {"dailyData": [
    {"date": "2026-06-20", "platformMetrics": {"instagram": {"reach": 155, "likes": 7, "shares": 1, "saves": 1, "views": 251, "postCount": 5}}},
]}


def _index(rows):
    return {(r["platform"], r["metric_date"]): r for r in rows}


def test_followers_snapshot_y_actividad_reales():
    rows = _index(build_snapshot_rows(DAILY, ACCOUNTS, "c_mb", "prof_mb", "2026-06-22"))
    ig_snap = rows[("instagram", "2026-06-22")]      # snapshot followers de hoy
    assert ig_snap["followers"] == 2 and ig_snap["reach"] is None   # followers sí, actividad de hoy None
    ig_act = rows[("instagram", "2026-06-20")]       # actividad del día real
    assert ig_act["reach"] == 155 and ig_act["likes"] == 7 and ig_act["followers"] is None


def test_cero_real_se_guarda_ausente_es_none():
    """0 que Zernio reportó = dato real (se guarda 0) · key ausente = None (NUNCA 0 fabricado)."""
    rows = _index(build_snapshot_rows(DAILY, ACCOUNTS, "c_mb", "prof_mb", "2026-06-22"))
    tt = rows[("tiktok", "2026-06-22")]
    assert tt["followers"] == 0          # 0 REAL de Zernio (tiktok tiene 0 followers) → se guarda
    ig_act = rows[("instagram", "2026-06-20")]
    assert ig_act["comments"] is None    # Zernio no mandó comments ese día → None, NO 0 fabricado


def test_anti_fabricacion_sin_dato_sin_fila():
    """EL test del arco: negocio sin dato Zernio → CERO filas (no una fila de 0s)."""
    assert build_snapshot_rows({}, [], "c_x", "prof_x", "2026-06-22") == []
    # accounts de otro profile + daily vacío → sigue 0 filas (nada del profile pedido)
    assert build_snapshot_rows({}, ACCOUNTS, "c_x", "prof_AUSENTE", "2026-06-22") == []


def test_aislamiento_client_id_y_profile():
    """Cada fila lleva el client_id pedido · la cuenta ajena (prof_or, 99) NO entra."""
    rows = build_snapshot_rows(DAILY, ACCOUNTS, "c_mb", "prof_mb", "2026-06-22")
    assert all(r["client_id"] == "c_mb" for r in rows)              # todas de MB
    assert all(r["followers"] != 99 for r in rows)                 # el 99 de OR jamás
    plats = {r["platform"] for r in rows}
    assert plats == {"instagram", "facebook", "tiktok"}            # solo las de prof_mb


def test_cuenta_sin_dato_no_crea_fila_vacia():
    """Cuenta sin followersCount NI actividad → NO fila (jamás una fila toda-None · solo dato real
    crea fila). Si tuviera actividad otro día, esa fila sí existe con followers None honesto."""
    accs = [{"_id": "ig", "platform": "instagram", "profileId": "prof_mb"}]  # sin followersCount
    assert build_snapshot_rows({}, accs, "c_mb", "prof_mb", "2026-06-22") == []
