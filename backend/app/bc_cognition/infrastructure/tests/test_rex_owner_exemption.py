"""Tests · exención cuenta-dueño en el gating REX (migr 00074 · owner_accounts).

Garantías:
  - add-on EFECTIVO = almacenado OR cuenta-dueño exenta (no hace falta comprar el add-on).
  - el TOGGLE (autonomous_mode_on) sigue mandando aparte: dueño con toggle OFF NO publica.
  - aislamiento: la exención de un dueño NO contamina a clientes ajenos.
El fake de supabase honra .eq → reproduce el filtro server-side del toggle.
"""
from types import SimpleNamespace

import pytest

import app.bc_cognition.infrastructure.rex_publish_repository as repo
import app.bc_cognition.infrastructure.owner_accounts_repository as owners

OWNER = "u-owner"
OTHER = "u-other"


class _Q:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = list(rows)

    def select(self, *a: object, **k: object) -> "_Q":
        return self

    def limit(self, *a: object, **k: object) -> "_Q":
        return self

    def eq(self, col: str, val: object) -> "_Q":
        self._rows = [r for r in self._rows if r.get(col) == val]
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=[dict(r) for r in self._rows])


class _Client:
    def __init__(self, tables: dict[str, list[dict[str, object]]]) -> None:
        self._tables = tables

    def table(self, name: str) -> _Q:
        return _Q(self._tables.get(name, []))


def _wire(monkeypatch: pytest.MonkeyPatch, clients: list[dict[str, object]],
          owner_ids: list[str]) -> None:
    monkeypatch.setattr(repo, "_sb", lambda: _Client({"clients": clients}))
    monkeypatch.setattr(owners, "_sb",
                        lambda: _Client({"owner_accounts": [{"user_id": u} for u in owner_ids]}))


def _client(cid: str, uid: str, addon: bool, toggle: bool) -> dict[str, object]:
    return {"id": cid, "rex_addon_active": addon, "user_id": uid,
            "autonomous_mode_on": toggle, "crisis_active": False, "reseller_id": None}


def test_exento_toggle_on_entra_y_addon_efectivo(monkeypatch: pytest.MonkeyPatch) -> None:
    # Cuenta-dueño SIN add-on comprado pero toggle ON → entra al universo · addon EFECTIVO=True → publica.
    _wire(monkeypatch, [_client("c-own", OWNER, addon=False, toggle=True)], [OWNER])
    assert repo.fetch_active_rex_client_ids() == ["c-own"]
    g = repo.fetch_client_gating("c-own")
    assert g is not None and g["rex_addon_active"] is True and g["autonomous_mode_on"] is True


def test_exento_toggle_off_no_publica(monkeypatch: pytest.MonkeyPatch) -> None:
    # CRÍTICO: dueño con toggle OFF · addon EFECTIVO=True PERO el toggle manda aparte → NO publica.
    # Sin "toggle filtra aparte" (punto i) este test cae primero: el dueño entraría al universo.
    _wire(monkeypatch, [_client("c-own", OWNER, addon=False, toggle=False)], [OWNER])
    assert repo.fetch_active_rex_client_ids() == []          # toggle OFF → fuera del universo
    g = repo.fetch_client_gating("c-own")
    assert g is not None and g["rex_addon_active"] is True   # exención efectiva...
    assert not (g["rex_addon_active"] and g["autonomous_mode_on"])  # ...pero NO publica (toggle)


def test_normal_sin_addon_sigue_holdeado(monkeypatch: pytest.MonkeyPatch) -> None:
    # Cliente NO dueño, sin add-on, toggle ON → addon EFECTIVO=False → fuera del universo · holdea.
    _wire(monkeypatch, [_client("c-free", OTHER, addon=False, toggle=True)], [OWNER])
    assert repo.fetch_active_rex_client_ids() == []
    g = repo.fetch_client_gating("c-free")
    assert g is not None and g["rex_addon_active"] is False


def test_aislamiento_owner_no_contamina_otros(monkeypatch: pytest.MonkeyPatch) -> None:
    # Dos clientes toggle ON: el del dueño entra por exención · el ajeno NO (no es dueño, sin addon).
    _wire(monkeypatch, [_client("c-own", OWNER, addon=False, toggle=True),
                        _client("c-free", OTHER, addon=False, toggle=True)], [OWNER])
    assert repo.fetch_active_rex_client_ids() == ["c-own"]


def test_helper_efectivo_es_una_sola_verdad() -> None:
    # is_rex_addon_effective = la regla compartida (worker + endpoint la reusan · no se duplica).
    assert owners.is_rex_addon_effective(False, OWNER, {OWNER}) is True   # exento por dueño
    assert owners.is_rex_addon_effective(True, OTHER, set()) is True      # add-on real en columna
    assert owners.is_rex_addon_effective(False, OTHER, {OWNER}) is False  # ni dueño ni add-on
