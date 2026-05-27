"""Núcleo de scraping · async httpx + bs4 (lxml) · sin DB · sin Claude.

Anti-SSRF: follow_redirects=False (más estricto que fetch_url_tool, que SÍ los
sigue) → un redirect a recurso interno no se sigue. Guardia de host interno
(localhost/IP privada/metadata) vía is_public_host · DEBT-075 (compartida con
fetch_url_tool).
Honesto: nunca lanza · retorna {"ok": False, "error": ...} ante fallo. Parse puro en
_parse_html (CPU breve · 1 página · smoke-testeable directo · sin red).
"""
from __future__ import annotations
import re
from collections import Counter
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.infrastructure.tools._url_safety import is_public_host

_TIMEOUT = 15.0
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OmegaBot/1.0; +https://r-omega.agency)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es,en;q=0.9",
}
_MAX_HEADINGS = 10
_WORD_RE = re.compile(r"[a-záéíóúüñ]+", re.IGNORECASE)
_STOPWORDS = set(
    "el la los las de del que y en un una para con por su al lo como más pero sus "
    "le ya o este esta sí no se es son tu te nos muy the".split()
)


async def analyze_website(url: str) -> dict[str, Any]:
    """Fetch + parse de una URL pública · retorna dict honesto (nunca lanza)."""
    # Anti-SSRF — DEBT-075: rechaza loopback / IP privada / metadata cloud.
    if not is_public_host(url):
        return {"ok": False, "error": "Host no público (SSRF bloqueado)"}
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT, follow_redirects=False, headers=_HEADERS
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        return {"ok": False, "error": f"HTTP {e.response.status_code}"}
    except httpx.TimeoutException:
        return {"ok": False, "error": f"Timeout (sin respuesta en {int(_TIMEOUT)}s)"}
    except Exception as e:  # red, DNS, redirect-no-seguido, etc.
        return {"ok": False, "error": str(e)[:200]}
    return _parse_html(resp.text)


def _headings(soup: BeautifulSoup, tag: str) -> list[str]:
    out: list[str] = []
    for el in soup.find_all(tag):
        text = el.get_text(strip=True)
        if text:
            out.append(text)
        if len(out) >= _MAX_HEADINGS:
            break
    return out


def _keywords(soup: BeautifulSoup) -> list[str]:
    words = (w.lower() for w in _WORD_RE.findall(soup.get_text(" ")))
    counts = Counter(w for w in words if len(w) > 3 and w not in _STOPWORDS)
    return [w for w, _ in counts.most_common(10)]


def _score_and_recs(
    title: str, meta: str, h1: list[str], h2: list[str], keywords: list[str]
) -> tuple[int, list[str]]:
    # (condición presente, recomendación si falta) · +20 por cada check OK.
    checks = [
        (bool(title), "Falta el <title> de la página"),
        (bool(meta), "Agregá una meta description (resumen de 150-160 caracteres)"),
        (bool(h1), "Tu página no tiene un H1 (título principal)"),
        (bool(h2), "Agregá subtítulos H2 (ej. con tu ciudad o servicio)"),
        (len(keywords) >= 5, "Poco contenido textual indexable"),
    ]
    score = sum(20 for ok, _ in checks if ok)
    recs = [msg for ok, msg in checks if not ok]
    return min(score, 100), recs


def _parse_html(html: str) -> dict[str, Any]:
    """Parse puro de HTML → dict de análisis (sin red · smoke-testeable)."""
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""
    meta_el = soup.find("meta", attrs={"name": "description"})
    meta = (meta_el.get("content") or "").strip() if meta_el else ""
    h1, h2, h3 = _headings(soup, "h1"), _headings(soup, "h2"), _headings(soup, "h3")
    keywords = _keywords(soup)
    score, recs = _score_and_recs(title, meta, h1, h2, keywords)
    return {
        "ok": True, "title": title, "meta_description": meta,
        "h1": h1, "h2": h2, "h3": h3, "keywords": keywords,
        "score": score, "recommendations": recs,
    }
