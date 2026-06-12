"""BUG 2 (11 jun) · las 3 cuentas test owner bypasean los gates de plan.

reseller@omega.com recibió `variations_require_pro_plan` (403) porque el gate
chequeaba el plan del client TARGET, no del email logueado. Política: bypass
por email. Este test fija el contrato del helper que el gate consulta."""
from app.bc_billing.domain.test_accounts import is_unrestricted_test_account


def test_las_3_cuentas_test_bypassean():
    assert is_unrestricted_test_account("cliente@omega.com")
    assert is_unrestricted_test_account("reseller@omega.com")
    assert is_unrestricted_test_account("zafaconesr@gmail.com")


def test_case_insensitive_y_trim():
    assert is_unrestricted_test_account("Reseller@Omega.com")
    assert is_unrestricted_test_account("  cliente@omega.com  ")


def test_cuentas_reales_no_bypassean():
    assert not is_unrestricted_test_account("cliente.real@gmail.com")
    assert not is_unrestricted_test_account("otro@omega.com")


def test_email_ausente_no_bypassea():
    assert not is_unrestricted_test_account(None)
    assert not is_unrestricted_test_account("")
