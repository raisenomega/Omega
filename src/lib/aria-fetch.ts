import { apiBase, authHeaders, handleResponse } from "./api-client";

// Fetch con timeout DEDICADO a ARIA (POST /aria/message + GET /aria/history). NO se aplica
// a apiPost/apiGet globales para no cortar generación de Content Lab/imagen (>35s legítimos).
// 35s > MAX_CLAUDE_LATENCY_MS (30s · limits_omega) → no corta respuestas válidas de ARIA.
//
// Clave (fix deadlock · hallazgo 🟡-1): el body (res.json en handleResponse) se lee DENTRO
// del mismo AbortController, no solo los headers. Si Railway entrega 200 pero el body queda
// colgado, el abort rechaza la lectura → la promesa settla → react-query baja isPending →
// el input se libera. Sin esto, el cuelgue de body tras los 200 headers seguiría mudo.
const ARIA_TIMEOUT_MS = 35_000;

async function ariaRequest<T>(path: string, init: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ARIA_TIMEOUT_MS);
  try {
    const res = await fetch(`${apiBase()}${path}`, { ...init, signal: controller.signal });
    return await handleResponse<T>(res);
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error("ARIA tardó demasiado (35s). Reintentá.");
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

export async function ariaGet<T>(path: string): Promise<T> {
  return ariaRequest<T>(path, { headers: await authHeaders() });
}

export async function ariaPost<T>(path: string, body: unknown): Promise<T> {
  return ariaRequest<T>(path, {
    method: "POST", headers: await authHeaders(), body: JSON.stringify(body),
  });
}
