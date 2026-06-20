"""Test CAMBIO 2 (dogfood ARIA): insert_client hereda default_client_aria_level del reseller.

override seteado (ej. Test Reseller=4) → el cliente nuevo nace con ese aria_level ·
override NULL (otros resellers, ej. OMEGA Direct) → se omite → DEFAULT del DB (1). No afecta a otros.
"""
import pytest

import app.api.routes.clients_v3._clients_repository as repo


class _Exec:
    def __init__(self, data: list) -> None:
        self.data = data


class _Q:
    def __init__(self, store: dict, table: str) -> None:
        self.store = store
        self.table_name = table

    def select(self, *a: object, **k: object) -> "_Q":
        return self

    def eq(self, *a: object, **k: object) -> "_Q":
        return self

    def limit(self, *a: object, **k: object) -> "_Q":
        return self

    def insert(self, row: dict) -> "_Q":
        self.store["insert"] = row
        return self

    def execute(self) -> _Exec:
        if self.table_name == "resellers":
            return _Exec([{"default_client_aria_level": self.store["override"]}])
        return _Exec([{"id": "new-client-id"}])


class _Client:
    def __init__(self, store: dict) -> None:
        self.store = store

    def table(self, name: str) -> _Q:
        return _Q(self.store, name)


def _patch(monkeypatch: pytest.MonkeyPatch, override: object) -> dict:
    store: dict = {"override": override}
    monkeypatch.setattr(repo, "_sb", lambda: _Client(store))
    return store


def test_insert_client_inherits_override(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch(monkeypatch, override=4)
    cid = repo.insert_client("u1", "r1", {"name": "Biz"})
    assert cid == "new-client-id"
    assert store["insert"]["aria_level"] == 4          # heredó el nivel del reseller
    assert store["insert"]["reseller_id"] == "r1"


def test_insert_client_no_override_omits_aria(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch(monkeypatch, override=None)
    repo.insert_client("u1", "r1", {"name": "Biz"})
    assert "aria_level" not in store["insert"]          # cae al DEFAULT del DB (1) · no afecta a otros
