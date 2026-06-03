// Carga universal de issues de cualquier fuente SENTINEL, normalizados a NormalizedIssue.
// Reusa endpoints existentes (history/latest/status · cero backend de lectura nuevo).
// El dispatcher rutea por source_type → loader específico (P1: shape real por fuente).
import { apiGet } from "@/lib/api-client";
import type { SentinelHistoryData, DependencyScan, SentinelScan } from "@/hooks/useSecurityDevData";
import type { RLSAudit } from "@/hooks/useRLSAudit";
import type { SecretRotation } from "@/hooks/useSecretsRotation";
import { loadRuntime, loadPerformance, loadAgentsHealth, loadAIProvider, loadNetworkHttp, loadIntegrations, loadChaos } from "./sentinel_issue_loaders_status";

export interface IssueAction { action: string; created_at: string; reason: string | null; }
export interface NormalizedIssue {
  key: string;
  severity: string;
  type: string;
  message: string;
  agentCode?: string;
  sourceType: string;
  sourceId: string | null;
  previousActions: IssueAction[];
}
export interface LoadParams { sourceType: string; sourceId?: string | null; severity?: string; agentCode?: string; }
// Params para abrir el modal universal desde cualquier chip (incluye scopeLabel para el título).
export interface OpenIssuesParams extends LoadParams { scopeLabel?: string; }

async function loadScan(severity?: string, agentCode?: string): Promise<NormalizedIssue[]> {
  const data = await apiGet<SentinelHistoryData>("/sentinel/history/");
  // Último scan POR agente (no el último run global · cadencias distintas — PULSE 5min vs VAULT 2 AM —
  // no deben ocultar issues de un agente que no esté en el bucket más reciente).
  const sorted = [...(data.scans ?? [])].sort((a, b) => (a.created_at < b.created_at ? 1 : -1));
  const latestByAgent = new Map<string, SentinelScan>();
  for (const s of sorted) if (!latestByAgent.has(s.agent_code)) latestByAgent.set(s.agent_code, s);
  const selected = agentCode
    ? (latestByAgent.has(agentCode) ? [latestByAgent.get(agentCode) as SentinelScan] : [])
    : [...latestByAgent.values()];
  const issues = selected.flatMap((s) =>
    s.issues.map((it) => ({
      key: `scan|${s.agent_code}|${it.severity}|${it.type}`, severity: it.severity, type: it.type, message: it.message,
      agentCode: s.agent_code, sourceType: "sentinel_scan", sourceId: s.id, previousActions: it.previous_actions ?? [],
    })),
  );
  return severity ? issues.filter((i) => i.severity === severity) : issues;
}

async function loadDependency(): Promise<NormalizedIssue[]> {
  const latest = (await apiGet<{ latest: DependencyScan | null }>("/sentinel/dependency-scans/latest")).latest;
  if (!latest || latest.status === "passed") return [];
  return [{
    key: `dep|${latest.id}`, severity: "HIGH", type: "dependency_scan", sourceType: "dependency_scan", sourceId: latest.id, previousActions: [],
    message: `Scan ${latest.scan_type} falló${latest.github_run_id ? ` · run ${latest.github_run_id}` : ""}. Revisar el reporte en GitHub Actions.`,
  }];
}

async function loadRLS(severity?: string): Promise<NormalizedIssue[]> {
  const latest = (await apiGet<{ latest: RLSAudit | null }>("/sentinel/rls-audit/latest")).latest;
  if (!latest) return [];
  const issues = latest.issues.map((it) => ({
    key: `rls|${it.table}|${it.issue_type}`, severity: it.severity, type: it.issue_type, message: `${it.table}: ${it.detail}`,
    sourceType: "rls_audit", sourceId: latest.id, previousActions: [],
  }));
  return severity ? issues.filter((i) => i.severity === severity) : issues;
}

async function loadSecrets(severity?: string): Promise<NormalizedIssue[]> {
  const secrets = (await apiGet<{ secrets: SecretRotation[] }>("/sentinel/secrets-rotation/status")).secrets ?? [];
  const issues = secrets
    .filter((s) => s.urgency === "urgent" || s.urgency === "warn")
    .map((s) => ({
      key: `sec|${s.secret_name}`, severity: s.urgency, type: "rotation_due", sourceType: "secrets_rotation", sourceId: null, previousActions: [],
      message: `${s.secret_name}: ${s.last_rotated_at ? `${s.days_since}d desde la última rotación (máx ${s.max_days}d)` : "sin rotación registrada"}`,
    }));
  return severity ? issues.filter((i) => i.severity === severity) : issues;
}

export async function loadIssuesBySource(p: LoadParams): Promise<NormalizedIssue[]> {
  switch (p.sourceType) {
    case "sentinel_scan": return loadScan(p.severity, p.agentCode);
    case "dependency_scan": return loadDependency();
    case "rls_audit": return loadRLS(p.severity);
    case "secrets_rotation": return loadSecrets(p.severity);
    case "runtime_observability": return loadRuntime(p.severity);
    case "performance": return loadPerformance(p.severity);
    case "agents_health": return loadAgentsHealth(p.agentCode);
    case "ai_provider_router": return loadAIProvider();
    case "network_http": return loadNetworkHttp(p.severity);
    case "integrations": return loadIntegrations(p.severity);
    case "chaos": return loadChaos(p.severity);
    default: return [];
  }
}
