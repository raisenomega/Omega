// Genera el prompt contextualizado de [Fix] por source_type · frontend = single source of truth.
// El backend solo persiste y devuelve lo que recibe. Sin emojis (regla OMEGA). El prompt se
// precarga en Dev Chat para que el operador lo dispare contra Claude (placeholder hasta DEBT-106).
import type { NormalizedIssue } from "./sentinel_issue_loaders";

const ref = (i: NormalizedIssue) => (i.sourceId ? ` · ref ${i.sourceId}` : "");

type Builder = (i: NormalizedIssue) => string;

const BUILDERS: Record<string, Builder> = {
  sentinel_scan: (i) => `Fix needed en ${i.agentCode}: severity=${i.severity}, type=${i.type}, message="${i.message}", scan_id=${i.sourceId ?? "n/a"}.`,
  dependency_scan: (i) => {
    const pkg = i.type.replace(/^(npm|bandit):/, "");
    const cmd = i.type.startsWith("npm:")
      ? `npm install ${pkg}@<versión-fix> (o npm audit fix · ojo bumps semver-major)`
      : `revisar finding bandit ${pkg} (si es benigno: # nosec con justificación · o .banditrc)`;
    return `Vulnerabilidad de dependencia: ${i.type} · severity=${i.severity} · ${i.message}. Fix sugerido: ${cmd}.`;
  },
  rls_audit: (i) => `Issue de RLS: ${i.message} · severity=${i.severity}${ref(i)}. Proponer la política RLS correcta para esa tabla.`,
  runtime_observability: (i) => `Issue de runtime: type=${i.type} · severity=${i.severity} · contexto="${i.message}". Diagnosticar causa raíz del error recurrente.`,
  performance: (i) => `Issue de performance: type=${i.type} · "${i.message}". Proponer optimización (query/índice/bundle) y medir el impacto.`,
  agents_health: (i) => `Issue de salud del agente ${i.agentCode}: type=${i.type} · "${i.message}" · severity=${i.severity}. Revisar prompt/routing/datos del agente.`,
  secrets_rotation: (i) => `Rotación de secret pendiente: ${i.message} · urgency=${i.severity}. Rotar el secret y registrar la rotación en SENTINEL.`,
  ai_provider_router: (i) => `Falla del proveedor IA ${i.agentCode}: type=${i.type} · "${i.message}" · severity=${i.severity}. Revisar credenciales/circuit breaker/failover.`,
  network_http: (i) => `Issue de Red/HTTP: type=${i.type} · "${i.message}" · severity=${i.severity}. Proponer fix (header faltante en middleware/vercel.json · renovar cert TLS · endurecer CORS).`,
  integrations: (i) => `Issue de integraciones: type=${i.type} · "${i.message}" · severity=${i.severity}. Revisar (idempotencia X4 webhook_events.event_id UNIQUE · liveness Stripe · refresh de token OAuth en social_accounts).`,
  chaos: (i) => `Fallo de chaos test: escenario type=${i.type} · "${i.message}" · severity=${i.severity}. El sistema NO degradó graceful en ese escenario · investigar resiliencia (timeout/error-handling/idempotencia/RLS/rate-limit).`,
};

export function buildFixPrompt(issue: NormalizedIssue): string {
  const builder = BUILDERS[issue.sourceType];
  return builder ? builder(issue) : `Fix needed: ${issue.severity} · ${issue.type} · ${issue.message}${ref(issue)}.`;
}
