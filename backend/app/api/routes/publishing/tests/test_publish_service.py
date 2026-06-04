"""publish_scheduled_post · cablea Publicar Auto → Zernio. G9 exime tests.
adapter+resolver MOCKEADOS (NO postea a Zernio · no ensucia FB en el gate). Verifica la LINEA
DIVISORIA: config/precondicion → PublishGateError (queda pending, reintentable) · fallo REAL de
publicacion → mark_failed. + gate 'pending' + media faltante."""
import asyncio

import pytest

from app.api.routes.publishing import _publish_service as ps
from app.bc_cognition.infrastructure.zernio_adapter import ZernioPublishError
from app.bc_cognition.infrastructure.zernio_resolver import ZernioAccountResolutionError


class _Repo:
    """Fake repo · registra las transiciones de estado (publishing/published/failed)."""
    def __init__(self, post, platform="facebook"):
        self._post, self._platform, self.calls = post, platform, []
    def get_scheduled_post(self, pid): return self._post
    def get_account_platform(self, sid): return self._platform
    def get_content_text(self, cid): return "hola"
    def mark_publishing(self, pid): self.calls.append("publishing")
    def mark_published(self, pid, ppid): self.calls.append(("published", ppid)); return {}
    def mark_failed(self, pid, err): self.calls.append(("failed", err))


def _post(status="pending", sa="sa1", media=None):
    return {"id": "p1", "client_id": "c1", "status": status,
            "social_account_id": sa, "content_id": "ct1", "media_url": media}


async def _resolve_ok(platform, mapped): return "acc1"
async def _create_ok(**kw): return "zpost_1"


def _wire(monkeypatch, repo, resolve=_resolve_ok, create=_create_ok):
    monkeypatch.setattr(ps, "repo", repo)
    monkeypatch.setattr(ps, "resolve_account_id", resolve)
    monkeypatch.setattr(ps, "create_post", create)
    # F5/2b · get_zernio_account_id consulta Supabase · se aísla (None = sin mapeo per-negocio)
    monkeypatch.setattr(ps, "get_zernio_account_id", lambda *a, **k: None)


def test_happy_path_publica_y_marca_published(monkeypatch):
    repo = _Repo(_post())
    _wire(monkeypatch, repo)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and out.platform_post_id == "zpost_1"
    assert repo.calls == ["publishing", ("published", "zpost_1")]


def test_create_post_falla_va_a_failed(monkeypatch):
    repo = _Repo(_post())
    async def _boom(**kw): raise ZernioPublishError("zernio_400:rechazado")
    _wire(monkeypatch, repo, create=_boom)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False and "zernio_400" in (out.error or "")
    assert repo.calls == ["publishing", ("failed", "zernio_400:rechazado")]  # intento real → failed


def test_sin_cuenta_queda_pending_reintentable(monkeypatch):
    repo = _Repo(_post())
    async def _sin(platform, mapped): raise ZernioAccountResolutionError("zernio_sin_cuenta:facebook")
    _wire(monkeypatch, repo, resolve=_sin)
    with pytest.raises(ps.PublishGateError) as ei:
        asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert "zernio_sin_cuenta" in ei.value.code
    assert repo.calls == []  # NI publishing NI failed → el post sigue 'pending' (reintentable)


def test_cuenta_ambigua_queda_pending(monkeypatch):
    repo = _Repo(_post())
    async def _amb(platform, mapped): raise ZernioAccountResolutionError("zernio_cuenta_ambigua:facebook:2")
    _wire(monkeypatch, repo, resolve=_amb)
    with pytest.raises(ps.PublishGateError):
        asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert repo.calls == []  # queda pending · NUNCA adivina la cuenta (P2)


def test_media_faltante_ig_va_a_failed_sin_llamar_zernio(monkeypatch):
    repo = _Repo(_post(media=None), platform="instagram")
    called = {"create": False}
    async def _track(**kw): called["create"] = True; return "x"
    _wire(monkeypatch, repo, create=_track)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False and "zernio_media_requerida" in (out.error or "")
    assert called["create"] is False and repo.calls == [("failed", "zernio_media_requerida:instagram")]


def test_status_no_pending_gatea(monkeypatch):
    repo = _Repo(_post(status="published"))
    _wire(monkeypatch, repo)
    with pytest.raises(ps.PublishGateError):
        asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert repo.calls == []
