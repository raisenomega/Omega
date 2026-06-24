"""Tests · insert_brand_voice_corpus_approved NUNCA mete una URL al corpus.

Raíz: drafts de imagen guardan la URL en generated_text → al aprobar entraba al
corpus → scorer X5 medía contra URLs → score bajo a todo. El guard determinista
descarta URLs/vacío ANTES de insertar (no se aprende basura · mejor vacío).
"""
from types import SimpleNamespace

import app.api.routes.content_v3._content_repository as repo


class _Tbl:
    def __init__(self, store: dict) -> None:
        self.store = store

    def insert(self, row: dict) -> "_Tbl":
        self.store["inserts"].append(row)
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=[{"id": "x"}])


class _Client:
    def __init__(self, store: dict) -> None:
        self.store = store

    def table(self, name: str) -> _Tbl:
        self.store["tables"].append(name)
        return _Tbl(self.store)


def _patch(monkeypatch) -> dict:
    store: dict = {"inserts": [], "tables": []}
    monkeypatch.setattr(repo, "_sb", lambda: _Client(store))
    # sanitize_input passthrough (acción no-block · clean_text = el texto)
    monkeypatch.setattr(repo, "sanitize_input",
                        lambda text, ctx: (SimpleNamespace(action="ok", clean_text=text), None))
    return store


def test_url_text_not_inserted(monkeypatch) -> None:
    store = _patch(monkeypatch)
    repo.insert_brand_voice_corpus_approved(
        "cli-A", "https://x.supabase.co/storage/v1/object/public/generated-images/a.png", None)
    assert store["inserts"] == []          # URL → cero writes al corpus
    assert store["tables"] == []           # ni siquiera tocó la tabla


def test_empty_text_not_inserted(monkeypatch) -> None:
    store = _patch(monkeypatch)
    repo.insert_brand_voice_corpus_approved("cli-A", "   ", None)
    assert store["inserts"] == []


def test_real_caption_inserted_as_approved_draft(monkeypatch) -> None:
    store = _patch(monkeypatch)
    repo.insert_brand_voice_corpus_approved("cli-A", "Caption real de marca limpio", None)
    assert len(store["inserts"]) == 1
    row = store["inserts"][0]
    assert row["text"] == "Caption real de marca limpio"
    assert row["source"] == "approved_draft"
    assert row["client_id"] == "cli-A"
