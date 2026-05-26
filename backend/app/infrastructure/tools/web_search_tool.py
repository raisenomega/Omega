# backend/app/infrastructure/tools/web_search_tool.py
# MAX 200 LINES — R-LINES-001
# Web Search Tool — integración con Brave Search API
# R-MCP-001: toda búsqueda web pasa por este tool registrado

from __future__ import annotations
import os
import time
import httpx
from typing import Any

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
BRAVE_URL     = "https://api.search.brave.com/res/v1/web/search"
RATE_LIMIT_PER_HOUR = 60


async def web_search(
    query: str,
    agent_code: str,
    client_id: str | None = None,
    max_results: int = 3,
) -> dict[str, Any]:
    """
    Busca en internet via Brave Search API.
    Retorna resultados con título, URL, contenido y score de relevancia.
    R-LEGAL-001: fuente legal — no scraping directo.
    """
    if not BRAVE_API_KEY:
        return {
            "success": False,
            "error": "BRAVE_API_KEY no configurada en Railway",
            "results": []
        }

    if not query or len(query.strip()) < 3:
        return {
            "success": False,
            "error": "Query demasiado corta",
            "results": []
        }

    start = time.time()
    max_results = min(max(1, max_results), 5)  # clamp 1-5

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:  # 8s · si Brave tarda más → [] · ARIA no se bloquea
            response = await client.get(
                BRAVE_URL,
                params={
                    "q": query,
                    "count": max_results,
                    "search_lang": "es",
                    "country": "US",
                    "text_decorations": False,
                },
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": BRAVE_API_KEY,
                }
            )
            response.raise_for_status()
            data = response.json()

        duration_ms = int((time.time() - start) * 1000)

        results = []
        web_results = data.get("web", {}).get("results", [])
        for r in web_results:
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("description", "")[:1000],
                "score":   1.0,
            })

        answer = data.get("query", {}).get("altered", "")

        return {
            "success":  True,
            "query":    query,
            "answer":   answer,
            "results":  results,
            "count":    len(results),
            "duration_ms": duration_ms,
        }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"Brave HTTP {e.response.status_code}",
            "results": []
        }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Timeout — Brave no respondió en 8s",
            "results": []
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


def format_for_claude(result: dict[str, Any]) -> str:
    """Convierte resultado de web_search a texto legible para el agente."""
    if not result.get("success"):
        return f"[web_search ERROR]: {result.get('error', 'Error desconocido')}"

    lines = [f"[web_search] Query: {result['query']}"]

    if result.get("answer"):
        lines.append(f"Respuesta directa: {result['answer']}")

    for i, r in enumerate(result.get("results", []), 1):
        lines.append(f"\n{i}. {r['title']}")
        lines.append(f"   URL: {r['url']}")
        lines.append(f"   {r['content'][:300]}...")

    return "\n".join(lines)
