// SENTINEL Capa 9 · captura global de errores frontend → POST /sentinel/runtime/frontend-error.
// Throttle por signature (1/min) · keepalive · try/catch propio: el reporter NUNCA rompe la app
// ni entra en loop de errores-reportando-errores.
import { apiBase } from "./api-client";

const _lastSent: Record<string, number> = {};
const THROTTLE_MS = 60_000;

// Hash sync (djb2) suficiente para deduplicar · no necesita ser criptográfico.
function signatureOf(message: string, stack: string): string {
  const s = `${message}|${stack}`;
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0;
  return h.toString(16).padStart(8, "0");
}

function report(message: string, stack: string, url: string): void {
  try {
    const sig = signatureOf(message, stack);
    const now = Date.now();
    if (_lastSent[sig] && now - _lastSent[sig] < THROTTLE_MS) return;
    _lastSent[sig] = now;
    const body = JSON.stringify({
      message: message.slice(0, 1000),
      stack: stack.slice(0, 5000),
      url: url.slice(0, 500),
      user_agent: navigator.userAgent.slice(0, 500),
      signature: sig,
    });
    fetch(`${apiBase()}/sentinel/runtime/frontend-error`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    }).catch(() => {
      /* swallow · sin loop */
    });
  } catch {
    /* swallow · el reporter NUNCA rompe la app */
  }
}

export function reportError(error: unknown, info?: string): void {
  const e = error instanceof Error ? error : new Error(String(error));
  const url = typeof location !== "undefined" ? location.href : "";
  report(e.message + (info ? ` · ${info}` : ""), e.stack ?? "", url);
}

let _inited = false;
export function initErrorReporter(): void {
  if (_inited || typeof window === "undefined") return;
  _inited = true;
  window.addEventListener("error", (ev) => report(ev.message ?? "error", ev.error?.stack ?? "", location.href));
  window.addEventListener("unhandledrejection", (ev) => {
    const r = ev.reason as { message?: string; stack?: string } | undefined;
    report(r?.message ?? String(ev.reason), r?.stack ?? "", location.href);
  });
}
