"""publish_scheduled_post · cablea Publicar Auto → Zernio. G9 exime tests.
adapter+resolver MOCKEADOS (NO postea a Zernio · no ensucia FB en el gate). Verifica la LINEA
DIVISORIA: config/precondicion → PublishGateError (queda pending, reintentable) · fallo REAL de
publicacion → mark_failed. + gate 'pending' + media faltante."""
import asyncio

import pytest

from app.api.routes.publishing import _publish_service as ps
from app.bc_cognition.infrastructure import zernio_adapter as za
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


def _post(status="pending", sa="sa1", media=None, attempts=0, media_urls=None):
    return {"id": "p1", "client_id": "c1", "status": status, "attempts": attempts,
            "social_account_id": sa, "content_id": "ct1", "media_url": media, "media_urls": media_urls}


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
    # Gap-2 · HERMES usage-tracking · no-op por defecto (los tests específicos lo overridean para asertar).
    monkeypatch.setattr(ps, "record_mcp_use", lambda *a, **k: None)


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


# ── Gap-2 · HERMES ve el uso REAL de Zernio (record_mcp_use) ──
def test_hermes_registra_zernio_ok(monkeypatch):
    repo = _Repo(_post())
    rec = []
    _wire(monkeypatch, repo)
    monkeypatch.setattr(ps, "record_mcp_use", lambda integ, ok, detail=None: rec.append((integ, ok, detail)))
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True
    assert rec == [("zernio", True, None)]  # publicación real exitosa → ok=True


def test_hermes_registra_zernio_fallo_en_path_de_retry(monkeypatch):
    # Zernio 503 (transitorio → reintenta) · el intento fallido SE REGISTRA igual (señal honesta del retry).
    repo = _Repo(_post(attempts=0))
    rec = []
    async def _boom(**kw): raise ZernioPublishError("zernio_503:upstream", status_code=503)
    _wire(monkeypatch, repo, create=_boom)
    monkeypatch.setattr(ps, "record_mcp_use", lambda integ, ok, detail=None: rec.append((integ, ok, detail)))
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert (out.error or "").startswith("retry:")           # fue al path de reintento
    assert rec == [("zernio", False, "zernio_503:upstream")]  # y aún así registró el fallo real


def test_hermes_best_effort_no_rompe_el_publish(monkeypatch):
    # Si record_mcp_use LANZA, el guard lo traga → el publish NO se rompe (observabilidad ≠ camino crítico).
    repo = _Repo(_post())
    def _raise(*a, **k): raise RuntimeError("hermes down")
    _wire(monkeypatch, repo)
    monkeypatch.setattr(ps, "record_mcp_use", _raise)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and out.platform_post_id == "zpost_1"


def test_hermes_no_registra_bug_inesperado(monkeypatch):
    # Un bug NUESTRO (no ZernioError) NO ensucia la señal de Zernio · solo los ZernioError registran.
    repo = _Repo(_post())
    rec = []
    async def _bug(**kw): raise RuntimeError("bug nuestro")
    _wire(monkeypatch, repo, create=_bug)
    monkeypatch.setattr(ps, "record_mcp_use", lambda integ, ok, detail=None: rec.append((integ, ok, detail)))
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False and "unexpected" in (out.error or "")
    assert rec == []  # NO se registró uso de Zernio (no fue Zernio quien falló)


# ── B4 · DEBT-HERMES-TIKTOK-TITLE · truncar título SOLO TikTok-foto (video + IG/FB intactos) ──
def test_cap_tiktok_title_trunca_foto_largo():
    msg = "Tu zafacon huele peor que el problema que resuelve y todo el vecindario entero ya lo nota a metros hoy"
    out = ps._cap_tiktok_title(msg, "tiktok", "https://x.co/img.png")
    assert len(out) <= 90 and out.endswith("…")
    assert " " in out and not out[:-1].endswith(" ")          # limite de palabra, no corta a mitad


def test_cap_tiktok_title_foto_corto_sin_cambio():
    msg = "Caption corto bajo noventa"
    assert ps._cap_tiktok_title(msg, "tiktok", "https://x.co/img.png") == msg


def test_cap_tiktok_title_video_sin_cambio():
    assert ps._cap_tiktok_title("x" * 200, "tiktok", "https://x.co/clip.mp4") == "x" * 200   # video: sin cap


def test_cap_tiktok_title_ig_fb_intactos():
    msg = "x" * 200                                            # el caption largo que truncamos para TikTok
    assert ps._cap_tiktok_title(msg, "instagram", "https://x.co/img.png") == msg   # IG: entero
    assert ps._cap_tiktok_title(msg, "facebook",  "https://x.co/img.png") == msg   # FB: entero


# ── Pieza 3 · story/placement · platformSpecificData.contentType:"story" (STEP 0 en vivo) ──
# story SOLO en IG/FB (doc oficial) · filtro en OMEGA (nunca a redes sin story) · guard de ratio
# saltado cuando is_story (el 9:16 ES válido como historia · no lo matamos antes de Zernio).

def test_story_psd_instagram():
    assert ps.story_psd(True, "instagram") == {"contentType": "story"}


def test_story_psd_facebook():
    assert ps.story_psd(True, "facebook") == {"contentType": "story"}


def test_story_psd_tiktok_none():       # tiktok NO soporta story → filtro → None (post normal)
    assert ps.story_psd(True, "tiktok") is None


def test_story_psd_linkedin_none():     # linkedin NO soporta story → None
    assert ps.story_psd(True, "linkedin") is None


def test_story_psd_not_story_none():    # sin flag → None (retrocompat · flujo de hoy)
    assert ps.story_psd(False, "instagram") is None


# ── Fix dedup 24h Zernio · story REAL apenda sufijo único del id de la fila (STEP 0 diff-global=201) ──
# Zernio hashea (platform, accountId, content+media) · la story comparte media+cuenta con su feed-gemela
# → 409. Sufijo único por fila = fingerprint distinto SIEMPRE. SOLO story real (IG/FB): la story NO
# muestra el caption → invisible. Feed y TikTok-is_story (post normal · caption visible) → content INTACTO.
def test_story_dedup_content_ig_apenda_sufijo():
    assert ps.story_dedup_content("hola", True, "instagram", "abcd1234-ef56") == "hola ·abcd1234"


def test_story_dedup_content_fb_apenda_sufijo():
    assert ps.story_dedup_content("hola", True, "facebook", "deadbeef-0000") == "hola ·deadbeef"


def test_story_dedup_content_feed_intacto():            # is_story=false → content sin tocar (caption real)
    assert ps.story_dedup_content("hola", False, "instagram", "abcd1234") == "hola"


def test_story_dedup_content_tiktok_is_story_intacto():  # tiktok publica post NORMAL → sin sufijo (no leak)
    assert ps.story_dedup_content("hola", True, "tiktok", "abcd1234") == "hola"


def test_story_dedup_content_sufijo_unico_por_fila():    # cada fila su sufijo (deriva del id)
    a = ps.story_dedup_content("x", True, "instagram", "11111111-a")
    b = ps.story_dedup_content("x", True, "instagram", "22222222-b")
    assert a != b


def test_story_dedup_content_feed_vacia_sigue_distinta():  # feed="" vs story=""+sufijo → distintos
    assert ps.story_dedup_content("", True, "instagram", "abcd1234") == " ·abcd1234"
    assert ps.story_dedup_content("", False, "instagram", "abcd1234") == ""


def test_story_9x16_ig_salta_guard_y_manda_psd(monkeypatch):  # ANTI-SILENCIO #1+#2
    repo = _Repo({**_post(media="https://x/y.png"), "is_story": True}, platform="instagram")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zpost_s"
    _wire(monkeypatch, repo, create=_cap, ratio=0.5625)  # 9:16 · guard rechazaría si NO fuera story
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True
    assert cap["platforms"][0].get("platformSpecificData") == {"contentType": "story"}  # #2 · psd a Zernio
    assert repo.calls == ["publishing", ("published", "zpost_s")]           # #1 · guard NO marcó failed


def test_story_fb_manda_psd(monkeypatch):
    repo = _Repo({**_post(media="https://x/y.png"), "is_story": True}, platform="facebook")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap, ratio=0.5625)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["platforms"][0].get("platformSpecificData") == {"contentType": "story"}


def test_story_tiktok_psd_none_post_normal(monkeypatch):  # filtro: story marcada pero tiktok → psd None
    repo = _Repo({**_post(media="https://x/y.mp4"), "is_story": True}, platform="tiktok")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["platforms"][0].get("platformSpecificData") is None


def test_story_ig_content_lleva_sufijo(monkeypatch):  # fix dedup · story IG → content con sufijo del id
    repo = _Repo({**_post(media="https://x/y.png"), "is_story": True}, platform="instagram")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap, ratio=0.5625)
    asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert cap["content"] == "hola ·p1"  # message "hola" + " ·" + post_id[:8] (id="p1")


def test_feed_ig_content_sin_sufijo(monkeypatch):  # feed (no story) → content intacto (caption real)
    repo = _Repo(_post(media="https://x/y.png"), platform="instagram")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap, ratio=1.0)
    asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert cap["content"] == "hola"


def test_story_tiktok_content_sin_sufijo(monkeypatch):  # tiktok-is_story = post normal → caption sin sufijo
    repo = _Repo({**_post(media="https://x/y.mp4"), "is_story": True}, platform="tiktok")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap)
    asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert cap["content"] == "hola"


def test_no_story_ig_sin_psd(monkeypatch):  # retrocompat: sin flag → create_post SIN psd · guard corrió
    repo = _Repo(_post(media="https://x/y.png"), platform="instagram")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap, ratio=1.0)  # cuadrada · guard pasa
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["platforms"][0].get("platformSpecificData") is None


# ── Pieza 2 · carrusel · selección de media: media_urls (N) con fallback retrocompat a [media_url] ──
# El array media_urls (col 00080) lleva el carrusel completo. Precedencia: si está poblado → manda los N
# al adapter; si NULL/vacío → cae a [media_url] (filas previas a 00080 · comportamiento de HOY intacto).
def test_media_urls_array_manda_N(monkeypatch):  # carrusel: 3 media → el adapter recibe los 3, no 1
    urls = ["https://x/1.png", "https://x/2.png", "https://x/3.png"]
    repo = _Repo(_post(media="https://x/1.png", media_urls=urls), platform="facebook")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["media_urls"] == urls  # los 3, no [media_url]


def test_media_urls_null_fallback_single(monkeypatch):  # fila vieja típica (media_urls NULL) → [media_url]
    repo = _Repo(_post(media="https://x/1.png", media_urls=None), platform="facebook")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["media_urls"] == ["https://x/1.png"]  # retrocompat dura


def test_media_urls_vacio_fallback_single(monkeypatch):  # [] (lista vacía) → [media_url] ([] or [u] = [u])
    repo = _Repo(_post(media="https://x/1.png", media_urls=[]), platform="facebook")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["media_urls"] == ["https://x/1.png"]


def test_sin_media_alguna_fb(monkeypatch):  # FB no exige media · ambos None → media_urls=None (path de hoy)
    repo = _Repo(_post(media=None, media_urls=None), platform="facebook")
    cap = {}
    async def _cap(**kw): cap.update(kw); return "zp"
    _wire(monkeypatch, repo, create=_cap)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and cap["media_urls"] is None


# ── Commit 5a · estado-mentira tipo A: timeout 40→120 + 409-already-posted = published (no failed) ──
# Bug confirmado 3 veces (03:06/07:06/22:00): el post sale a IG pero el timeout corta la respuesta →
# falso 'failed' + post_id perdido · el reintento da 409 dedup → hoy mark_failed (la DB miente).
_DUP_409 = ('zernio_409:{"error":"This exact content is already scheduled, publishing, or was '
            'posted to this account within the last 24 hours.","details":{"accountId":"x"}}')


def test_timeout_120():
    # El timeout subió 40→120s (carrusel de 5 placas SIEMPRE tarda >40s · cabe en la ventana del cron 300s).
    assert za._HTTP_TIMEOUT == 120.0


def test_409_already_posted_es_published(monkeypatch):
    # El reintento recibe el 409 dedup 24h → el contenido YA salió antes → mark_published HONESTO (no failed) ·
    # post_id=None (el timeout lo comió). Cierra el estado-mentira: la DB deja de decir 'failed' sobre un post real.
    repo = _Repo(_post(attempts=1))
    async def _dup(**kw): raise ZernioPublishError(_DUP_409, status_code=409)
    _wire(monkeypatch, repo, create=_dup)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and out.platform_post_id is None
    assert repo.calls == ["publishing", ("published", None)]  # PUBLISHED, no failed


def test_otro_error_no_es_published(monkeypatch):
    # Anti falso-positivo: un 400 terminal NO es el dedup → sigue failed · un timeout de transporte → retry.
    # NINGUNO se marca published (solo el 409-already-posted exacto lo hace).
    repo400 = _Repo(_post(attempts=0))
    async def _b400(**kw): raise ZernioPublishError("zernio_400:contenido_invalido", status_code=400)
    _wire(monkeypatch, repo400, create=_b400)
    out400 = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out400.published is False
    assert repo400.calls == ["publishing", ("failed", "zernio_400:contenido_invalido")]
    assert ("published", None) not in repo400.calls

    repo_to = _Repo(_post(attempts=0))
    async def _to(**kw): raise ZernioPublishError("zernio_transport_error:ReadTimeout", transport=True)
    _wire(monkeypatch, repo_to, create=_to)
    out_to = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out_to.published is False and (out_to.error or "").startswith("retry:")  # timeout → retry, no published
    assert ("published", None) not in repo_to.calls


def test_409_distinto_no_published(monkeypatch):
    # SOLO el 409-already-posted exacto → published. Otro 409 (causa distinta) → failed honesto, NUNCA published.
    repo = _Repo(_post(attempts=0))
    other = 'zernio_409:{"error":"some other conflict"}'
    async def _other(**kw): raise ZernioPublishError(other, status_code=409)
    _wire(monkeypatch, repo, create=_other)
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is False
    assert repo.calls == ["publishing", ("failed", other)]  # otro 409 → failed, no published


def test_no_rompe_publish_normal(monkeypatch):
    # Cero regresión: publicación normal exitosa sigue marcando published con su post_id REAL.
    repo = _Repo(_post())
    _wire(monkeypatch, repo)  # _create_ok → "zpost_1"
    out = asyncio.run(ps.publish_scheduled_post("p1", "c1"))
    assert out.published is True and out.platform_post_id == "zpost_1"
    assert repo.calls == ["publishing", ("published", "zpost_1")]
