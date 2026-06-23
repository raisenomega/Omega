"""DEBT-047 fix · build_jobstore_url escapa el password (el @ que rompía create_engine → host @@...).
Prueba con password con @ Y # (escapa TODO, no solo el @). Pura · sin DB (create_engine solo parsea)."""
from sqlalchemy import create_engine

from app.infrastructure._jobstore_url import build_jobstore_url, pick_jobstore_url


def test_password_con_arroba_y_especiales_no_envenena_el_host():
    # password con @ (el bug) + # (otro especial) · host real detrás del ÚLTIMO @
    raw = "postgresql+psycopg2://user.abc:Pa@@ss#w0rd@db.host.com:6543/postgres"
    eng = create_engine(build_jobstore_url(raw))   # parsea · NO conecta
    assert eng.url.host == "db.host.com"            # host CORRECTO · no "@@db.host.com" (el bug)
    assert eng.url.password == "Pa@@ss#w0rd"        # password completo preservado (con @ y #)
    assert eng.url.username == "user.abc"
    assert eng.url.port == 6543
    assert eng.url.database == "postgres"


def test_cruda_sin_arroba_sigue_funcionando():
    raw = "postgresql+psycopg2://u:simple@h.com:5432/db"
    eng = create_engine(build_jobstore_url(raw))
    assert eng.url.host == "h.com" and eng.url.password == "simple"


def test_no_parseable_devuelve_raw_para_que_el_caller_caiga_a_in_memory():
    # si no matchea, devuelve el raw → create_engine/el try-except del caller decide (red intacta)
    assert build_jobstore_url("not-a-postgres-url") == "not-a-postgres-url"
    assert build_jobstore_url("") == ""


def test_pick_override_gana_cuando_esta():
    assert pick_jobstore_url("postgresql://direct:5432/db", "postgresql://pooler:6543/db") == "postgresql://direct:5432/db"


def test_pick_cae_al_default_cuando_override_vacio():
    assert pick_jobstore_url("", "postgresql://pooler:6543/db") == "postgresql://pooler:6543/db"
    assert pick_jobstore_url("   ", "postgresql://pooler:6543/db") == "postgresql://pooler:6543/db"  # blanco → default


def test_pick_ambos_vacios_da_vacio_para_que_el_caller_devuelva_none():
    # ambos vacíos → "" → en _persistent_jobstore_or_none `if not raw: return None` → in-memory (igual que antes)
    assert pick_jobstore_url("", "") == ""
    assert pick_jobstore_url(None, None) == ""
