// Carga universal de issues SENTINEL → NormalizedIssue. Reusa endpoints existentes (cero backend
// de lectura nuevo) · dispatcher rutea por source_type → loader específico (P1: shape real por fuente).
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
  // Último scan POR agente (no el último run global · cadencias distintas no deben ocultar issues).
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

interface DepJsVuln { name: string; severity: string; range?: string; title?: string; direct?: boolean; cvss?: number | null; fix?: string; }
interface DepPyFinding { id: string; severity: string; file?: string; line?: number; text?: string; noise?: boolean; }
const JS_SEV: Record<string, string> = { critical: "CRITICAL", high: "HIGH", moderate: "MEDIUM", low: "LOW" };

async function loadDependency(severity?: string): Promise<NormalizedIssue[]> {
  const latest = (await apiGet<{ latest: DependencyScan | null }>("/sentinel/dependency-scans/latest")).latest;
  if (!latest) return [];
  const s = (latest.summary ?? {}) as { js?: { vulns?: DepJsVuln[] }; python?: { findings?: DepPyFinding[] } };
  const base = { sourceType: "dependency_scan", sourceId: latest.id, previousActions: [] } as const;
  const issues: NormalizedIssue[] = (s.js?.vulns ?? []).map((v) => ({
    ...base, key: `dep|js|${v.name}`, severity: JS_SEV[v.severity] ?? (v.severity || "MEDIUM").toUpperCase(), type: `npm:${v.name}`,
    message: `${v.title || "vuln"} · range ${v.range ?? "?"} · fix → ${v.fix ?? "?"}${v.direct ? " · directa" : " · transitiva"}${v.cvss ? ` · CVSS ${v.cvss}` : ""}`,
  }));
  for (const f of s.python?.findings ?? []) issues.push({
    ...base, key: `dep|py|${f.id}|${f.line}`, severity: f.severity || "MEDIUM", type: `bandit:${f.id}`,
    message: `${f.file ?? "?"}:${f.line ?? "?"} · ${f.text ?? ""}${f.noise ? " · low-noise (test/standard · accepted)" : ""}`,
  });
  if (!issues.length && latest.status && latest.status !== "passed")
    issues.push({ ...base, key: `dep|${latest.id}`, severity: "HIGH", type: "dependency_scan", message: `Scan ${latest.scan_type} status=${latest.status} (sin desglose · re-correr workflow).` });
  return severity ? issues.filter((i) => i.severity === severity) : issues;
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
    case "dependency_scan": return loadDependency(p.severity);
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
