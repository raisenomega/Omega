// Labels §8 para el tab HERMES · español de negocio, CERO snake_case/jerga en pantalla.

const INTEGRATION_LABELS: Record<string, string> = {
  anthropic: "Anthropic (texto/ARIA)",
  nano_banana: "Generación de imágenes",
  veo3: "Generación de video",
  voyage: "Memoria semántica",
  brave: "Búsqueda web",
  stripe: "Pagos",
  resend: "Emails",
  zernio: "Zernio (publicación)",
};

// Consola del proveedor para ir a actuar (abre en pestaña nueva · GEMINI key = AI Studio).
const INTEGRATION_URLS: Record<string, string> = {
  anthropic: "https://console.anthropic.com",
  nano_banana: "https://aistudio.google.com/app/apikey",
  veo3: "https://aistudio.google.com/app/apikey",
  voyage: "https://dashboard.voyageai.com",
  brave: "https://api-dashboard.search.brave.com",
  stripe: "https://dashboard.stripe.com",
  resend: "https://resend.com/overview",
  zernio: "https://dashboard.zernio.com",
};

// Umbral del amarillo POR integración (minutos): 'ok' con last_use más viejo = "Sin uso reciente".
const YELLOW_MIN: Record<string, number> = {
  anthropic: 60, brave: 180, voyage: 360, stripe: 1440, resend: 1440,
  nano_banana: 10080, veo3: 30240,  // 7d · 21d
  zernio: 1440,  // 1d
};

interface StatusInfo { label: string; cls: string; rank: number; meaning: string }  // rank: severidad (0 arriba)

const GRAY = "text-muted-foreground bg-muted/30 border-border/40";
const STATUS_LABELS: Record<string, StatusInfo> = {
  last_use_failed:  { label: "Falló el último uso", cls: "text-red-500 bg-red-500/15 border-red-500/40", rank: 0, meaning: "La credencial está, pero la última llamada real falló." },
  sin_uso_reciente: { label: "Sin uso reciente", cls: "text-amber-500 bg-amber-500/15 border-amber-500/40", rank: 1, meaning: "Operativa, pero hace rato que no se usa." },
  ok:               { label: "Operativo", cls: "text-emerald-500 bg-emerald-500/15 border-emerald-500/40", rank: 2, meaning: "Configurada y respondiendo; último uso OK." },
  sin_uso:          { label: "Sin uso registrado", cls: GRAY, rank: 3, meaning: "Operativa; aún no se registró ningún uso real." },
  no_configurado:   { label: "Sin configurar", cls: GRAY, rank: 4, meaning: "Falta la credencial en el entorno." },
};

function humanize(raw: string): string {
  const c = raw.replace(/_/g, " ").trim();
  return c.charAt(0).toUpperCase() + c.slice(1);
}

export function integrationLabel(code: string): string {
  return INTEGRATION_LABELS[code] ?? humanize(code);
}

export function integrationUrl(code: string): string | null {
  return INTEGRATION_URLS[code] ?? null;
}

// Estado VISUAL derivado: el amarillo NO existe en la DB (status es ok/no_configurado/last_use_failed).
// 'ok' sin last_use = sin uso registrado (gris · ausencia de señal) · 'ok' + last_use viejo = amarillo.
export function effectiveStatus(it: { integration: string; status: string; last_use: string | null }): string {
  if (it.status !== "ok") return it.status;
  if (!it.last_use) return "sin_uso";
  const ageMin = (Date.now() - new Date(it.last_use).getTime()) / 60000;
  return ageMin > (YELLOW_MIN[it.integration] ?? Infinity) ? "sin_uso_reciente" : "ok";
}

export function statusInfo(status: string): StatusInfo {
  return STATUS_LABELS[status] ?? { label: humanize(status), cls: GRAY, rank: 5, meaning: "" };
}
