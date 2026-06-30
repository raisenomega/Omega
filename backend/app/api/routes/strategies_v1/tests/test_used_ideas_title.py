"""REDISEÑO Estrategias Fase B.1 · used-ideas trae el TITULO de la estrategia de origen.
list_idea_usages: select('*, strategies(titulo)') → PostgREST anida {strategies:{titulo}} via el FK
strategy_id→strategies. Ownership (scope client_id) intacto. Titulo null defensivo (caso borde)."""
from unittest.mock import MagicMock
from app.bc_cognition.infrastructure import strategy_idea_usage_repository as usages


def _rows(sb):
    return sb.client.table.return_value.select.return_value.in_.return_value.order.return_value.limit.return_value.execute


def test_used_ideas_incluye_titulo():
    """El list pide el embed del titulo y lo devuelve anidado en cada item."""
    sb = MagicMock()
    _rows(sb).return_value.data = [{"id": "u1", "strategy_id": "s1", "brief": "idea", "strategies": {"titulo": "Mi estrategia"}}]
    out = usages.list_idea_usages(sb, ["biz1"])
    assert out[0]["strategies"]["titulo"] == "Mi estrategia"
    sb.client.table.return_value.select.assert_called_with("*, strategies(titulo)")


def test_used_ideas_scope_intacto():
    """El ownership (scope client_id) sigue en el WHERE con el embed · sin client_ids → []."""
    sb = MagicMock()
    _rows(sb).return_value.data = [{"id": "u1"}]
    usages.list_idea_usages(sb, ["biz1"])
    sb.client.table.return_value.select.return_value.in_.assert_called_with("client_id", ["biz1"])
    assert usages.list_idea_usages(MagicMock(), []) == []


def test_used_ideas_titulo_null_defensivo():
    """Caso borde: sin titulo (strategies null) → el item pasa tal cual, no rompe."""
    sb = MagicMock()
    _rows(sb).return_value.data = [{"id": "u1", "strategy_id": "s1", "strategies": None}]
    assert usages.list_idea_usages(sb, ["biz1"])[0]["strategies"] is None
