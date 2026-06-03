// Genera el prompt contextualizado de [Fix] por source_type · frontend = single source of truth.
// El backend solo persiste y devuelve lo que recibe. Sin emojis (regla OMEGA). El prompt se
// precarga en Dev Chat para que el operador lo dispare contra Claude (placeholder hasta DEBT-106).
import type { NormalizedIssue } from "./sentinel_issue_loaders";

const ref = (i: NormalizedIssue) => (i.sourceId ? ` · ref ${i.sourceId}` : "");

type Builder = (i: NormalizedIssue) => string;

const BUILDERS: Record<string, Builder> = {
  sentinel_scan: (i) => `Fix needed en ${i.agentCode}: severity=${i.severity}, type=${i.type}, message="${i.message}", scan_id=${i.sourceId ?? "n/a"}.`,
  dependency_scan: (i) => `Alerta de dependencias (CVE): ${i.message} · severity=${i.severity}. Revisar el run del GitHub Action y proponer bump/patch.`,
  rls_audit: (i) => `Issue de RLS: ${i.message} · severity=${i.severity}${ref(i)}. Proponer la política RLS correcta para esa tabla.`,
  runtime_observability: (i) => `Issue de runtime: type=${i.type} · severity=${i.severity} · contexto="${i.message}". Diagnosticar causa raíz del error recurrente.`,
  performance: (i) => `Issue de performance: type=${i.type} · "${i.message}". Proponer optimización (query/índice/bundle) y medir el impacto.`,
  agents_health: (i) => `Issue de salud del agente ${i.agentCode}: type=${i.type} · "${i.message}" · severity=${i.severity}. Revisar prompt/routing/datos del agente.`,
  secrets_rotation: (i) => `Rotación de secret pendiente: ${i.message} · urgency=${i.severity}. Rotar el secret y registrar la rotación en SENTINEL.`,
  ai_provider_router: (i) => `Falla del proveedor IA ${i.agentCode}: type=${i.type} · "${i.message}" · severity=${i.severity}. Revisar credenciales/circuit breaker/failover.`,
};

export function buildFixPrompt(issue: NormalizedIssue): string {
  const builder = BUILDERS[issue.sourceType];
  return builder ? builder(issue) : `Fix needed: ${issue.severity} · ${issue.type} · ${issue.message}${ref(issue)}.`;
}
