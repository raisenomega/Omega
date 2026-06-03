// Loaders de issues para las fuentes "status" (runtime/performance/agents-health/ai-providers).
// Reusan los endpoints existentes (cero backend de lectura nuevo · AP-OMEGA-005). P1: si una
// fuente no tiene issues estructurados, se normaliza lo que SÍ tiene (counts/calls reales).
import { apiGet } from "@/lib/api-client";
import type { RuntimeStatus } from "@/hooks/useRuntimeStatus";
import type { PerformanceStatus } from "@/hooks/usePerformanceStatus";
import type { AgentsHealthStatus } from "@/hooks/useAgentsHealthStatus";
import type { AIProvidersStatus } from "@/hooks/useAIProvidersStatus";
import type { NetworkHTTPStatus } from "@/hooks/useNetworkHTTPStatus";
import type { IntegrationsStatus } from "@/hooks/useIntegrationsStatus";
import type { ChaosStatus } from "@/hooks/useChaosStatus";
import type { NormalizedIssue } from "./sentinel_issue_loaders";

const bySeverity = (issues: NormalizedIssue[], severity?: string) =>
  severity ? issues.filter((i) => i.severity === severity) : issues;

export async function loadRuntime(severity?: string): Promise<NormalizedIssue[]> {
  const scan = (await apiGet<RuntimeStatus>("/sentinel/runtime/status")).last_scan;
  if (!scan) return [];
  const issues = scan.issues.map((it) => ({ severity: it.severity, type: it.check, message: it.detail }));
  const rec = scan.recurring_patterns.map((r) => ({ severity: "MEDIUM", type: "recurring_pattern", message: `${r.source}: ${r.sample} (x${r.count})` }));
  return bySeverity([...issues, ...rec].map((x, i) => ({ key: `rt|${i}|${x.type}`, ...x, sourceType: "runtime_observability", sourceId: null, previousActions: [] })), severity);
}

export async function loadPerformance(severity?: string): Promise<NormalizedIssue[]> {
  const scan = (await apiGet<PerformanceStatus>("/sentinel/performance/status")).last_scan;
  if (!scan) return [];
  const issues = scan.issues.map((it) => ({ severity: it.severity, type: it.check, message: it.detail }));
  const slow = scan.slow_queries.map((q) => ({ severity: "MEDIUM", type: "slow_query", message: `${q.mean_ms}ms x${q.calls} · ${q.query.slice(0, 80)}` }));
  return bySeverity([...issues, ...slow].map((x, i) => ({ key: `pf|${i}|${x.type}`, ...x, sourceType: "performance", sourceId: null, previousActions: [] })), severity);
}

export async function loadAgentsHealth(agentCode?: string): Promise<NormalizedIssue[]> {
  const scan = (await apiGet<AgentsHealthStatus>("/sentinel/agents-health/status")).last_scan;
  if (!scan) return [];
  const drift = scan.model_drift_alerts.map((d) => ({ severity: "HIGH", type: "model_drift", message: `${d.agent}: esperado ${d.expected}, actual ${d.actual}`, agentCode: d.agent }));
  const low = scan.per_agent
    .filter((a) => a.success_rate != null && a.success_rate < 0.95)
    .map((a) => ({ severity: "MEDIUM", type: "low_success_rate", message: `${a.agent_code}: success_rate ${Math.round((a.success_rate ?? 0) * 100)}% en ${a.calls_24h} calls`, agentCode: a.agent_code }));
  const all = [...drift, ...low].map((x, i) => ({ key: `ah|${i}|${x.agentCode}`, ...x, sourceType: "agents_health", sourceId: null, previousActions: [] }));
  return agentCode ? all.filter((i) => i.agentCode === agentCode) : all;
}

export async function loadNetworkHttp(severity?: string): Promise<NormalizedIssue[]> {
  const data = await apiGet<NetworkHTTPStatus>("/sentinel/network-http/status");
  const issues = (data.targets ?? []).flatMap((t) =>
    (t.last_scan?.issues ?? []).map((it, i) => ({
      key: `net|${t.url}|${i}|${it.check}`, severity: it.severity, type: it.check, message: it.detail,
      sourceType: "network_http", sourceId: t.last_scan?.id ?? null, previousActions: [],
    })),
  );
  return severity ? issues.filter((i) => i.severity === severity) : issues;
}

export async function loadIntegrations(severity?: string): Promise<NormalizedIssue[]> {
  const scan = (await apiGet<IntegrationsStatus>("/sentinel/integrations/status")).last_scan;
  if (!scan) return [];
  const issues = scan.issues.map((it, i) => ({
    key: `int|${i}|${it.check}`, severity: it.severity, type: it.check, message: it.detail,
    sourceType: "integrations", sourceId: scan.id, previousActions: [],
  }));
  return severity ? issues.filter((x) => x.severity === severity) : issues;
}

export async function loadChaos(severity?: string): Promise<NormalizedIssue[]> {
  const data = await apiGet<ChaosStatus>("/sentinel/chaos/status");
  const issues = (data.scenarios ?? []).flatMap((s) =>
    (s.issues ?? []).map((it, i) => ({
      key: `chaos|${s.scenario}|${i}`, severity: it.severity, type: it.check, message: it.detail,
      sourceType: "chaos", sourceId: s.id, previousActions: [],
    })),
  );
  return severity ? issues.filter((x) => x.severity === severity) : issues;
}

export async function loadAIProvider(): Promise<NormalizedIssue[]> {
  const data = await apiGet<AIProvidersStatus>("/sentinel/ai-providers/status");
  const out: NormalizedIssue[] = [];
  for (const p of data.providers) {
    if (p.circuit_state === "open")
      out.push({ key: `ai|circuit|${p.name}`, severity: "CRITICAL", type: "circuit_open", message: `${p.name}: circuit breaker abierto (${p.consecutive_failures} fallos seguidos)`, agentCode: p.name, sourceType: "ai_provider_router", sourceId: null, previousActions: [] });
    if (p.last_24h.failed > 0)
      out.push({ key: `ai|failed|${p.name}`, severity: "HIGH", type: "failed_calls", message: `${p.name}: ${p.last_24h.failed} llamadas fallidas de ${p.last_24h.total_calls} en 24h`, agentCode: p.name, sourceType: "ai_provider_router", sourceId: null, previousActions: [] });
  }
  return out;
}
