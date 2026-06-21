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
    def mark_retry(self, pid, attempts, err):  # transitorio · simula la persistencia (vuelve a pending)
        self.calls.append(("retry", attempts)); self._post["attempts"] = attempts; self._post["status"] = "pending"


def _post(status="pending", sa="sa1", media=None, attempts=0):
    return {"id": "p1", "client_id": "c1", "status": status, "attempts": attempts,
            "social_account_id": sa, "content_id": "ct1", "media_url": media}


async def _resolve_ok(platform, mapped): return "acc1"
async def _create_ok(**kw): return "zpost_1"


def _wire(monkeypatch, repo, resolve=_resolve_ok, create=_create_ok, ratio=None):
    monkeypatch.setattr(ps, "repo", repo)
    monkeypatch.setattr(ps, "resolve_account_id", resolve)
    monkeypatch.setattr(ps, "create_post", create)
    # F5/2b · get_zernio_account_id consulta Supabase · se aísla (None = sin mapeo per-negocio)
    monkeypatch.setattr(ps, "get_zernio_account_id", lambda *a, **k: None)
    # Guard aspect ratio · se aísla la lectura del header (I/O). ratio=None → fail-open (no bloquea).
    async def _ratio(url): return ratio
    monkeypatch.setattr(ps, "fetch_image_ratio", _ratio)


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


def test_aspect_9x16_ig_falla_honesto(monkeypatch):  # guard: vertical → IG feed → failed honesto
    repo = _Repo(_post(media="https://x/y.png"), platform="instagram")
    called = {"create": False}
    async def _track(**kw): called["create"] = True; return "x"
    _wire(monkeypatch, repo, create=_track, ratio=0.5625)  # 9:16
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False and "imagen_vertical_no_apta_feed_ig" in (out.error or "")
    assert "zernio_400" not in (out.error or "")  # NO el mensaje enganoso de Zernio
    assert called["create"] is False  # NUNCA llega a Zernio
    assert repo.calls == [("failed", out.error)]  # esa fila → failed honesto


def test_aspect_9x16_tiktok_pasa(monkeypatch):  # tiktok leniente · vertical OK
    repo = _Repo(_post(media="https://x/y.png"), platform="tiktok")
    _wire(monkeypatch, repo, ratio=0.5625)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True
    assert repo.calls == ["publishing", ("published", "zpost_1")]


def test_aspect_1x1_ig_pasa(monkeypatch):  # cuadrada → IG feed OK
    repo = _Repo(_post(media="https://x/y.png"), platform="instagram")
    _wire(monkeypatch, repo, ratio=1.0)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True
    assert repo.calls == ["publishing", ("published", "zpost_1")]


# Fan-out mixto (IG vertical falla · TikTok pasa) = composicion de los dos tests de arriba:
# cada fila del fan-out es un publish_scheduled_post independiente → una falla NO aborta la otra.


def test_status_no_pending_gatea(monkeypatch):
    repo = _Repo(_post(status="published"))
    _wire(monkeypatch, repo)
    with pytest.raises(ps.PublishGateError):
        asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert repo.calls == []


# ── Gap-1 · reintento de fallos TRANSITORIOS de Zernio (no perder el post) ──
def test_transitorio_5xx_reintenta_y_publica_al_segundo(monkeypatch):
    # 1er intento: Zernio 503 (transitorio) → mark_retry (queda pending, NO failed) · 2º intento: publica.
    repo = _Repo(_post(attempts=0))
    n = {"i": 0}
    async def _flaky(**kw):
        n["i"] += 1
        if n["i"] == 1:
            raise ZernioPublishError("zernio_503:upstream", status_code=503)
        return "zpost_2"
    _wire(monkeypatch, repo, create=_flaky)
    out1 = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out1.published is False and (out1.error or "").startswith("retry:")
    assert repo.calls == ["publishing", ("retry", 1)]            # reintentable · NO failed
    out2 = asyncio.run(ps.publish_scheduled_post("p1", "c1"))    # REX lo retoma (sigue pending)
    assert out2.published is True and out2.platform_post_id == "zpost_2"
    assert repo.calls == ["publishing", ("retry", 1), "publishing", ("published", "zpost_2")]


def test_terminal_4xx_va_a_failed_sin_reintentar(monkeypatch):
    # 400 (contenido/media rechazada) = terminal · reintentar no ayuda → failed directo, JAMAS retry.
    repo = _Repo(_post(attempts=0))
    async def _boom(**kw): raise ZernioPublishError("zernio_400:contenido_invalido", status_code=400)
    _wire(monkeypatch, repo, create=_boom)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False and "zernio_400" in (out.error or "")
    assert repo.calls == ["publishing", ("failed", "zernio_400:contenido_invalido")]
    assert all(c[0] != "retry" for c in repo.calls if isinstance(c, tuple))  # nunca reintenta terminal


def test_transitorio_con_tope_agotado_va_a_failed(monkeypatch):
    # attempts=2 → este es el 3º (== MAX_RETRIES) · transitorio pero tope agotado → failed (no loop infinito).
    repo = _Repo(_post(attempts=2))
    async def _boom(**kw): raise ZernioPublishError("zernio_503:upstream", status_code=503)
    _wire(monkeypatch, repo, create=_boom)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False and "zernio_503" in (out.error or "")
    assert repo.calls == ["publishing", ("failed", "zernio_503:upstream")]  # tope → failed, corta el loop
