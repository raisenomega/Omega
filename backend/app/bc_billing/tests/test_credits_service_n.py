"""A2.3 · check_budget_for_n · pre-check por-N (regla 80% con colchón · un carrusel no agota el día).
Separado de test_credits_service por el techo C4 (aquél ya está en 99/100). Reusa su _patch. G9 exime tests."""
import asyncio

from app.bc_billing.tests.test_credits_service import _patch
from app.bc_billing.application.credits_service import check_budget_for_n


def test_alcanza_para_n():
    # restante 5 · 6×0.05=0.30 <= 0.80×5=4.0 → True (alcanza)
    with _patch({"rows": [{"budget_usd_mensual": 5, "consumido_usd": 0}]}):
        assert asyncio.run(check_budget_for_n("c1", 6)) is True


def test_no_alcanza_para_n():
    # restante 0.30 · 10×0.05=0.50 > 0.80×0.30=0.24 → False (bloquea · no genera carrusel a medias)
    with _patch({"rows": [{"budget_usd_mensual": 0.30, "consumido_usd": 0}]}):
        assert asyncio.run(check_budget_for_n("c1", 10)) is False


def test_colchon_20_porciento():
    # restante 0.50 · 9×0.05=0.45 · CABRÍA sin colchón (0.45<0.50) pero 0.45 > 0.80×0.50=0.40 → False
    with _patch({"rows": [{"budget_usd_mensual": 0.50, "consumido_usd": 0}]}):
        assert asyncio.run(check_budget_for_n("c1", 9)) is False  # el colchón del 20% es el punto


def test_fail_open_no_enrolado():
    with _patch({"rows": []}):  # sin fila → True (fail-open · igual que check_budget)
        assert asyncio.run(check_budget_for_n("c1", 10)) is True


def test_route_premium():
    # restante 0.70 · premium 0.10: 6×0.10=0.60 > 0.80×0.70=0.56 → False · default 0.05: 0.30 <= 0.56 → True
    with _patch({"rows": [{"budget_usd_mensual": 0.70, "consumido_usd": 0}]}):
        assert asyncio.run(check_budget_for_n("c1", 6, route="premium")) is False
        assert asyncio.run(check_budget_for_n("c1", 6)) is True  # confirma que usa el costo del route
