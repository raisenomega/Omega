"""Cuentas test owner · enterprise perpetuo · acceso total sin paywall.

Política (ESTADO_OMEGA §1 · 28 may): estas 3 cuentas NUNCA ven paywall ni
restricción de plan. Cualquier gate de plan/créditos debe exonerarlas por
EMAIL del usuario LOGUEADO — no por el plan del client target (un reseller
test puede generar para un client sin plan pro → el gate por client_id lo
bloqueaba · BUG 11 jun). Dominio puro (A2 · sin imports externos)."""
from typing import Final, Optional

UNRESTRICTED_TEST_EMAILS: Final[frozenset[str]] = frozenset({
    "cliente@omega.com",      # client Zafacones Ramos · plan enterprise perpetuo
    "reseller@omega.com",     # reseller plan enterprise
    "zafaconesr@gmail.com",   # Owner Ibrain · is_super_owner · OMEGA Direct
})


def is_unrestricted_test_account(email: Optional[str]) -> bool:
    """True si el email es una cuenta test owner (bypass de paywall/plan)."""
    return bool(email) and email.strip().lower() in UNRESTRICTED_TEST_EMAILS
