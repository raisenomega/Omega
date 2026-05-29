"""Mapeo UI->DB de status del listado de contenido (incluye tab Papelera).
Test puro del dict (sin DB ni HTTP). G9 exime tests."""
from app.api.routes.content_v3.handlers.list_content import UI_TO_DB_STATUS


def test_rejected_mapea_a_rejected():
    # Papelera: status=rejected debe ser valido (no 422) y filtrar por 'rejected'
    assert "rejected" in UI_TO_DB_STATUS
    assert UI_TO_DB_STATUS["rejected"] == "rejected"


def test_mapeos_previos_intactos():
    # regresion: los tabs existentes no cambian
    assert UI_TO_DB_STATUS["pending"] == "draft"
    assert UI_TO_DB_STATUS["saved"] == "approved"
    assert UI_TO_DB_STATUS["all"] is None
