// Deriva un resumen uniforme {tone,label,score,lastRun} por componente desde la data
// de sus hooks existentes. Lógica PURA (sin React) · alimenta los headers colapsados de
// "Estado por componente". Cero fetch nuevo: los datos llegan ya resueltos.
import type { SentinelScan, DependencyScan } from "@/hooks/useSecurityDevData";
import type { SecretRotation } from "@/hooks/useSecretsRotation";
import type { RLSAudit } from "@/hooks/useRLSAudit";
import type { AIProvidersStatus } from "@/hooks/useAIProvidersStatus";
import type { RuntimeScan } from "@/hooks/useRuntimeStatus";
import type { PerformanceScan } from "@/hooks/usePerformanceStatus";
import type { AgentsHealthScan } from "@/hooks/useAgentsHealthStatus";
import type { NetworkHTTPStatus } from "@/hooks/useNetworkHTTPStatus";
import type { IntegrationsStatus } from "@/hooks/useIntegrationsStatus";

export type Tone = "ok" | "warn" | "bad" | "none";
export interface ComponentSummary { tone: Tone; label: string; score: number | null; lastRun: string | null; }

export interface SummaryInput {
  scans: SentinelScan[];
  dependency: DependencyScan | null;
  secrets: SecretRotation[];
  rls: RLSAudit | null;
  aiProviders: AIProvidersStatus | undefined;
  runtime: RuntimeScan | null;
  performance: PerformanceScan | null;
  agentsHealth: AgentsHealthScan | null;
  network: NetworkHTTPStatus | undefined;
  integrations: IntegrationsStatus | undefined;
}

const NONE: ComponentSummary = { tone: "none", label: "sin corridas", score: null, lastRun: null };
const scoreTone = (s: number): Tone => (s >= 95 ? "ok" : s >= 80 ? "warn" : "bad");
const statusTone = (s: string): Tone =>
  s === "pass" || s === "passed" ? "ok" : s === "warning" || s === "warn" ? "warn" : "bad";

export function latestScanFor(scans: SentinelScan[], codes: string[]): SentinelScan | null {
  const matches = scans.filter((s) => codes.includes(s.agent_code));
  return matches.sort((a, b) => (a.created_at < b.created_at ? 1 : -1))[0] ?? null;
}

function scanSummary(scan: SentinelScan | null): ComponentSummary {
  if (!scan) return NONE;
  return { tone: statusTone(scan.status), label: scan.status, score: scan.security_score, lastRun: scan.created_at };
}

function scoreScanSummary(scan: { score: number; scanned_at: string | null } | null): ComponentSummary {
  if (!scan) return NONE;
  return { tone: scoreTone(scan.score), label: `score ${scan.score}`, score: scan.score, lastRun: scan.scanned_at };
}

function secretsSummary(secrets: SecretRotation[]): ComponentSummary {
  if (secrets.length === 0) return NONE;
  const urgent = secrets.filter((s) => s.urgency === "urgent").length;
  const warn = secrets.filter((s) => s.urgency === "warn").length;
  const dates = secrets.map((s) => s.last_rotated_at).filter((d): d is string => !!d).sort();
  const lastRun = dates.length > 0 ? dates[dates.length - 1] : null;
  const tone: Tone = urgent > 0 ? "bad" : warn > 0 ? "warn" : "ok";
  return { tone, label: urgent || warn ? `${urgent} urgentes · ${warn} warn` : "al día", score: null, lastRun };
}

function rlsSummary(rls: RLSAudit | null): ComponentSummary {
  if (!rls) return NONE;
  const tone: Tone = rls.total_issues === 0 ? "ok" : rls.severity_critical + rls.severity_high > 0 ? "bad" : "warn";
  return { tone, label: rls.total_issues === 0 ? "RLS limpio" : `${rls.total_issues} issues`, score: null, lastRun: rls.scanned_at ?? rls.created_at };
}

function networkSummary(net: NetworkHTTPStatus | undefined): ComponentSummary {
  if (!net || net.overall_score == null) return NONE;
  const lastRun = net.targets.find((t) => t.last_scan)?.last_scan?.scanned_at ?? null;
  return { tone: scoreTone(net.overall_score), label: `score ${net.overall_score}`, score: net.overall_score, lastRun };
}

function aiSummary(ai: AIProvidersStatus | undefined): ComponentSummary {
  if (!ai) return NONE;
  const open = ai.providers.some((p) => p.circuit_state === "open");
  const configured = ai.providers.filter((p) => p.configured).length;
  return { tone: open ? "bad" : "ok", label: open ? "circuito abierto" : `${configured}/${ai.providers.length} configurados`, score: null, lastRun: null };
}

export function buildSummaries(input: SummaryInput): Record<string, ComponentSummary> {
  return {
    VAULT: scanSummary(latestScanFor(input.scans, ["VAULT"])),
    PULSE_MONITOR: scanSummary(latestScanFor(input.scans, ["PULSE_MONITOR", "PULSE"])),
    DB_GUARDIAN: scanSummary(latestScanFor(input.scans, ["DB_GUARDIAN"])),
    DEPENDENCY_SCAN: input.dependency
      ? { tone: statusTone(input.dependency.status), label: input.dependency.status, score: null, lastRun: input.dependency.created_at }
      : NONE,
    SECRETS_ROTATION: secretsSummary(input.secrets),
    RLS_HARDENING: rlsSummary(input.rls),
    AI_PROVIDER_ROUTER: aiSummary(input.aiProviders),
    RUNTIME_OBSERVABILITY: scoreScanSummary(input.runtime),
    PERFORMANCE_APM: scoreScanSummary(input.performance),
    AGENTS_HEALTH: scoreScanSummary(input.agentsHealth),
    NETWORK_HTTP: networkSummary(input.network),
    INTEGRATIONS: scoreScanSummary(input.integrations?.last_scan ?? null),
  };
}
