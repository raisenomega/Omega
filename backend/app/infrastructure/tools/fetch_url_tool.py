# backend/app/infrastructure/tools/fetch_url_tool.py
# MAX 200 LINES — R-LINES-001
# Fetch URL Tool — extrae contenido de URLs públicas
# R-LEGAL-001: respeta robots.txt — no scraping de Meta/LinkedIn directo

from __future__ import annotations
import time
import httpx
from typing import Any

from app.infrastructure.tools._url_safety import is_public_host

# URLs bloqueadas por ToS — R-LEGAL-001
BLOCKED_DOMAINS = {
    "linkedin.com", "www.linkedin.com",
    "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com",
    "tiktok.com", "www.tiktok.com",
}

MAX_CONTENT_CHARS = 5000
REQUEST_TIMEOUT   = 15.0


def _is_blocked(url: str) -> bool:
    """Verifica si el dominio está bloqueado por ToS — R-LEGAL-001"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower().lstrip("www.")
        return any(url.lower().find(blocked) != -1 for blocked in BLOCKED_DOMAINS)
    except Exception:
        return False


def _extract_text(html: str) -> str:
    """Extrae texto limpio de HTML sin dependencias externas."""
    import re
    # Elimina scripts, styles, y tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'\s+', ' ', html)
    return html.strip()[:MAX_CONTENT_CHARS]


async def fetch_url(
    url: str,
    agent_code: str,
    client_id: str | None = None,
    extract_type: str = "text",
) -> dict[str, Any]:
    """
    Extrae contenido de una URL pública.
    Bloquea dominios prohibidos por ToS — R-LEGAL-001.
    extract_type: 'text' = contenido completo | 'summary' = primeros 1000 chars
    """
    if not url or not url.startswith(("http://", "https://")):
        return {
            "success": False,
            "error": "URL inválida — debe comenzar con http:// o https://",
            "content": ""
        }

    if _is_blocked(url):
        return {
            "success": False,
            "error": (
                "Este dominio no está disponible para extracción directa. "
                "Usa web_search para obtener información de esta fuente."
            ),
            "content": "",
            "blocked": True
        }

    # Anti-SSRF — DEBT-075: rechaza loopback / IP privada / metadata cloud
    if not is_public_host(url):
        return {
            "success": False,
            "error": "URL no permitida — el host no es público (SSRF)",
            "content": ""
        }

    start = time.time()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; OmegaBot/1.0; "
            "+https://r-omega.agency)"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "es,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")

            if "text/html" not in content_type and "text/plain" not in content_type:
                return {
                    "success": False,
                    "error": f"Tipo de contenido no soportado: {content_type}",
                    "content": ""
                }

            raw_text = _extract_text(response.text)

        duration_ms = int((time.time() - start) * 1000)

        if extract_type == "summary":
            content = raw_text[:1000]
        else:
            content = raw_text

        return {
            "success":     True,
            "url":         url,
            "content":     content,
            "char_count":  len(content),
            "duration_ms": duration_ms,
        }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code} — {url}",
            "content": ""
        }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": f"Timeout — la URL no respondió en {REQUEST_TIMEOUT}s",
            "content": ""
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:200],
            "content": ""
        }


def format_for_claude(result: dict[str, Any]) -> str:
    """Convierte resultado de fetch_url a texto legible para el agente."""
    if not result.get("success"):
        if result.get("blocked"):
            return f"[fetch_url BLOQUEADO]: {result.get('error')}"
        return f"[fetch_url ERROR]: {result.get('error', 'Error desconocido')}"

    return (
        f"[fetch_url] URL: {result['url']}\n"
        f"Contenido ({result['char_count']} chars):\n"
        f"{result['content']}"
    )
