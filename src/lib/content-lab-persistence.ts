import type { ResultV2 } from "@/components/content/ResultCardV2";

// Cache de results POR NEGOCIO · aísla la grilla del Content Lab entre negocios del mismo dueño.
// Clave scopeada: `${LS_PREFIX}:<businessId>` · la global legacy (LS_PREFIX sin sufijo) se limpia 1 vez.
const LS_PREFIX = "omega_content_lab_results";
const MAX_PERSISTED = 20;

function keyFor(businessId: string): string { return `${LS_PREFIX}:${businessId}`; }

export function loadPersistedResults(businessId: string | null): ResultV2[] {
  if (!businessId) return [];  // sin negocio activo → nada (la página muestra EmptyState)
  try {
    localStorage.removeItem(LS_PREFIX);  // limpieza única del cache global legacy (sin sufijo · idempotente)
    const raw = localStorage.getItem(keyFor(businessId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function persistResults(businessId: string | null, results: ResultV2[]): void {
  if (!businessId) return;  // no escribir cache sin negocio
  try {
    const completed = results.filter(r => r.status !== "pending");
    const recent = completed.slice(-MAX_PERSISTED);
    localStorage.setItem(keyFor(businessId), JSON.stringify(recent));
  } catch {
    // localStorage full/disabled/private mode · silent skip
  }
}
