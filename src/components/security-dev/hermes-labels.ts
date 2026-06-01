// Labels §8 para el tab HERMES · español de negocio, CERO snake_case/jerga en pantalla
// (aunque el panel lo vea solo el super_owner, la regla aplica · patrón de learning-labels.ts).

const INTEGRATION_LABELS: Record<string, string> = {
  anthropic: "Anthropic (texto/ARIA)",
  nano_banana: "Generación de imágenes",
  veo3: "Generación de video",
  voyage: "Memoria semántica",
  brave: "Búsqueda web",
  stripe: "Pagos",
  resend: "Emails",
};

interface StatusInfo { label: string; cls: string; rank: number }  // rank: orden de severidad (0 = arriba)

const STATUS_LABELS: Record<string, StatusInfo> = {
  last_use_failed: { label: "Falló el último uso", cls: "text-red-500 bg-red-500/15 border-red-500/40", rank: 0 },
  ok:              { label: "Operativo",           cls: "text-emerald-500 bg-emerald-500/15 border-emerald-500/40", rank: 1 },
  no_configurado:  { label: "Sin configurar",      cls: "text-muted-foreground bg-muted/30 border-border/40", rank: 2 },
};

function humanize(raw: string): string {
  const c = raw.replace(/_/g, " ").trim();
  return c.charAt(0).toUpperCase() + c.slice(1);
}

export function integrationLabel(code: string): string {
  return INTEGRATION_LABELS[code] ?? humanize(code);  // nunca snake_case crudo
}

export function statusInfo(status: string): StatusInfo {
  return STATUS_LABELS[status] ?? { label: humanize(status), cls: "text-muted-foreground bg-muted/30 border-border/40", rank: 3 };
}
