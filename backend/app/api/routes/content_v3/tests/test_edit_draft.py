"""PATCH /content/{id}/draft · edita generated_text y/o metadata.fecha_sugerida (MERGE) en status=draft.
Mock de reader/repo · cero DB real. G9 exime tests. Fecha futura usa 2099 (siempre futura · sin mockear time)."""
import asyncio
from contextlib import ExitStack
from unittest.mock import patch, AsyncMock

from fastapi import HTTPException

from app.api.routes.content_v3 import _content_repository as repo
from app.api.routes.content_v3.handlers import edit_draft as h

_META = {"supervisado": True, "platform": "instagram", "origen": "aria_tool", "fecha_sugerida": "2026-06-01T10:00:00-04:00"}
_ITEM = {"id": "c1", "client_id": "client-A", "status": "draft", "generated_text": "old", "metadata": dict(_META)}


def _run(body, item=None, tz="America/Puerto_Rico"):
    """Corre el handler con reader/repo mockeados · devuelve (respuesta, args_del_write)."""
    cap = {}
    with ExitStack() as s:
        s.enter_context(patch.object(h, "get_current_user", AsyncMock(return_value={"id": "u1"})))
        s.enter_context(patch.object(h.reader, "get_content_item", return_value=(item if item is not None else dict(_ITEM, metadata=dict(_META)))))
        s.enter_context(patch.object(h.reader, "get_accessible_client_ids", return_value=["client-A"]))
        s.enter_context(patch.object(h.reader, "get_client_timezone", return_value=tz))
        s.enter_context(patch.object(h.repo, "update_draft_fields", lambda cid, text, meta: cap.update(args=(cid, text, meta))))
        out = asyncio.run(h.edit_draft("c1", body, "Bearer x"))
    return out, cap.get("args")


def _expect(body, code, item=None):
    try:
        _run(body, item=item)
        assert False, f"esperaba {code}"
    except HTTPException as e:
        assert e.status_code == code


def test_repo_update_draft_fields_solo_columnas_presentes():
    """Write parcial: text-only no manda metadata · meta-only no manda generated_text · vacio no ejecuta."""
    caps = []
    chain = type("C", (), {"update": lambda self, p: caps.append(p) or self, "eq": lambda self, *a: self, "execute": lambda self: None})()
    with patch.object(repo, "_sb", return_value=type("S", (), {"table": lambda self, n: chain})()):
        repo.update_draft_fields("c1", "hola", None)
        repo.update_draft_fields("c1", None, {"k": 1})
        repo.update_draft_fields("c1", None, None)  # no-op → cero execute
    assert caps == [{"generated_text": "hola"}, {"metadata": {"k": 1}}]


def test_404_no_existe():
    with patch.object(h, "get_current_user", AsyncMock(return_value={"id": "u1"})), \
         patch.object(h.reader, "get_content_item", return_value=None):
        try:
            asyncio.run(h.edit_draft("c1", h.EditDraftRequest(generated_text="x"), "Bearer x"))
            assert False
        except HTTPException as e:
            assert e.status_code == 404


def test_403_cliente_ajeno():
    _expect(h.EditDraftRequest(generated_text="x"), 403, item=dict(_ITEM, client_id="OTRO"))


def test_409_no_es_draft():
    _expect(h.EditDraftRequest(generated_text="x"), 409, item=dict(_ITEM, status="approved", metadata=dict(_META)))


def test_editar_solo_caption_no_toca_metadata():
    out, args = _run(h.EditDraftRequest(generated_text="nuevo caption"))
    assert args == ("c1", "nuevo caption", None)  # metadata=None → repo no la toca
    assert out["generated_text"] == "nuevo caption"


def test_caption_vacio_400():
    _expect(h.EditDraftRequest(generated_text="   "), 400)


def test_body_vacio_400():
    _expect(h.EditDraftRequest(), 400)


def test_fecha_futura_mergea_preservando_claves():
    out, args = _run(h.EditDraftRequest(scheduled_for="2099-06-15T15:00"))
    _, text, meta = args
    assert text is None  # solo se edito la fecha
    assert meta["supervisado"] is True and meta["platform"] == "instagram" and meta["origen"] == "aria_tool"
    assert meta["fecha_sugerida"].startswith("2099-06-15T15:00")  # offset-aware (tz cliente)
    assert out["scheduled_for"].startswith("2099-06-15T15:00")


def test_fecha_pasada_422():
    _expect(h.EditDraftRequest(scheduled_for="2000-01-01T00:00"), 422)


def test_fecha_null_borra_fecha_preserva_resto():
    out, args = _run(h.EditDraftRequest(scheduled_for=None))
    _, _, meta = args
    assert "fecha_sugerida" not in meta
    assert meta["supervisado"] is True and meta["platform"] == "instagram"
    assert out["scheduled_for"] is None
