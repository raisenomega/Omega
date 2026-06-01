// Etiquetas de cliente para la pestaña Aprendizaje ("Qué aprendió ARIA").
// REGLA (ESTADO_OMEGA): vistas de cara al cliente renderizan español de negocio · CERO jerga
// técnica (snake_case, agent_code, nombres de tabla/evento). Mapeo crudo→ES vive acá (fuente
// única · patrón de aria-levels.ts). Crudo sin mapeo → fallback legible, NUNCA snake_case.

const DECISION_LABELS: Record<string, string> = {
  generated_not_saved: "Propuse contenido que no se usó",
  approved_by_client: "Acertó: contenido aprobado",
  // [failed:...] NO se etiqueta: se excluye de la pestaña (isInternalErrorDecision · no es aprendizaje).
};

const OUTCOME_LABELS: Record<string, string> = {
  draft_abandoned_72h: "Borrador no publicado en 72h",
};

// agent_code → nombre de negocio. Cubre nova/aria (no están en tabla agents) + los demás en ES.
const AGENT_LABELS: Record<string, string> = {
  nova: "Tu asistente",          // NOVA es interna · nunca se nombra al cliente
  aria: "ARIA",
  brand_voice: "Voz de marca",
  content_creator: "Creador de contenido",
};

// Eventos de PLOMERÍA INTERNA que NO son aprendizajes de ARIA (fallo de infra/API) → se excluyen
// de la pestaña del cliente: un error técnico no es algo que ARIA "decidió" ni "acertó/erró".
// No se borran de agent_memory · solo no se muestran ni cuentan en accuracy. (P2: no exponer fallos.)
export function isInternalErrorDecision(raw: string): boolean {
  return raw.startsWith("[failed:");
}

// Fallback: convierte un crudo técnico desconocido en algo legible (sin snake_case ni símbolos).
// Ej. "draft_abandoned_72h" → "Draft abandoned 72h" · "completion=90%" → "Completion 90%".
function humanize(raw: string): string {
  const cleaned = raw.replace(/[_=]+/g, " ").replace(/\s+/g, " ").trim();
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

export function labelDecision(raw: string): string {
  if (DECISION_LABELS[raw]) return DECISION_LABELS[raw];
  // perfil completado (completion=NN%) · patrón con valor variable
  const m = raw.match(/^completion=(\d+)%$/);
  if (m) return `Perfil completado al ${m[1]}%`;
  // texto que ya es natural (frase larga con espacios) → pasa tal cual
  if (/\s/.test(raw) && !/[_=]/.test(raw)) return raw;
  return humanize(raw);
}

export function labelOutcome(raw: string | null): string | null {
  if (!raw) return null;
  if (OUTCOME_LABELS[raw]) return OUTCOME_LABELS[raw];
  if (/\s/.test(raw) && !/[_=]/.test(raw)) return raw;
  return humanize(raw);
}

// Prioridad: etiqueta ES de negocio → nombre de la tabla agents (si vino) → humanize del code.
// NUNCA devuelve agent_code crudo en snake_case.
export function labelAgent(code: string, tableName?: string): string {
  if (AGENT_LABELS[code]) return AGENT_LABELS[code];
  if (tableName && tableName.trim()) return tableName;
  return /[_]/.test(code) ? humanize(code) : code;
}
