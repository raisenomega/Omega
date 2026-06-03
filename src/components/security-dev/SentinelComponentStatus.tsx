import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSentinelHistory, useDependencyScans } from "@/hooks/useSecurityDevData";
import { useSecretsRotationStatus } from "@/hooks/useSecretsRotation";
import { useRLSAuditLatest } from "@/hooks/useRLSAudit";
import { useAIProvidersStatus } from "@/hooks/useAIProvidersStatus";
import { useRuntimeStatus } from "@/hooks/useRuntimeStatus";
import { usePerformanceStatus } from "@/hooks/usePerformanceStatus";
import { useAgentsHealthStatus } from "@/hooks/useAgentsHealthStatus";
import { useNetworkHTTPStatus } from "@/hooks/useNetworkHTTPStatus";
import { useIntegrationsStatus } from "@/hooks/useIntegrationsStatus";
import { useChaosStatus } from "@/hooks/useChaosStatus";
import { SENTINEL_COMPONENTS } from "@/lib/sentinel_components_registry";
import { buildSummaries, latestScanFor } from "@/lib/sentinel_component_summary";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";
import { SentinelComponentRow } from "./SentinelComponentRow";
import { SentinelAgentCard } from "./SentinelAgentCard";
import { SentinelDependencyCard } from "./SentinelDependencyCard";
import { SentinelSecretsCard } from "./SentinelSecretsCard";
import { SentinelRLSCard } from "./SentinelRLSCard";
import { SentinelAIProvidersCard } from "./SentinelAIProvidersCard";
import { SentinelRuntimeCard } from "./SentinelRuntimeCard";
import { SentinelPerformanceCard } from "./SentinelPerformanceCard";
import { SentinelAgentsHealthCard } from "./SentinelAgentsHealthCard";
import { SentinelNetworkHTTPCard } from "./SentinelNetworkHTTPCard";
import { SentinelIntegrationsCard } from "./SentinelIntegrationsCard";
import { SentinelChaosCard } from "./SentinelChaosCard";

// "Estado por componente" · 10 filas colapsables. Header = resumen (status/score/última corrida);
// cuerpo = el card de detalle YA existente (reuso · React Query dedupea el fetch). Cero backend nuevo.
export function SentinelComponentStatus({ onOpenIssues }: { onOpenIssues: (p: OpenIssuesParams) => void }) {
  const scans = useSentinelHistory().data?.scans ?? [];
  const summaries = buildSummaries({
    scans,
    dependency: useDependencyScans().data?.latest ?? null,
    secrets: useSecretsRotationStatus().data?.secrets ?? [],
    rls: useRLSAuditLatest().data?.latest ?? null,
    aiProviders: useAIProvidersStatus().data,
    runtime: useRuntimeStatus().data?.last_scan ?? null,
    performance: usePerformanceStatus().data?.last_scan ?? null,
    agentsHealth: useAgentsHealthStatus().data?.last_scan ?? null,
    network: useNetworkHTTPStatus().data,
    integrations: useIntegrationsStatus().data,
    chaos: useChaosStatus().data,
  });

  const agentBody = (codes: string[]): ReactNode => {
    const scan = latestScanFor(scans, codes);
    return scan
      ? <SentinelAgentCard scan={scan} onOpenIssues={() => onOpenIssues({ sourceType: "sentinel_scan", agentCode: scan.agent_code, scopeLabel: scan.agent_code })} />
      : <p className="text-xs text-muted-foreground">Sin corridas aún · esperando primer cron.</p>;
  };
  const bodies: Record<string, ReactNode> = {
    VAULT: agentBody(["VAULT"]),
    PULSE_MONITOR: agentBody(["PULSE_MONITOR", "PULSE"]),
    DB_GUARDIAN: agentBody(["DB_GUARDIAN"]),
    DEPENDENCY_SCAN: <SentinelDependencyCard onOpenIssues={onOpenIssues} />,
    SECRETS_ROTATION: <SentinelSecretsCard onOpenIssues={onOpenIssues} />,
    RLS_HARDENING: <SentinelRLSCard onOpenIssues={onOpenIssues} />,
    AI_PROVIDER_ROUTER: <SentinelAIProvidersCard onOpenIssues={onOpenIssues} />,
    RUNTIME_OBSERVABILITY: <SentinelRuntimeCard onOpenIssues={onOpenIssues} />,
    PERFORMANCE_APM: <SentinelPerformanceCard onOpenIssues={onOpenIssues} />,
    AGENTS_HEALTH: <SentinelAgentsHealthCard onOpenIssues={onOpenIssues} />,
    NETWORK_HTTP: <SentinelNetworkHTTPCard onOpenIssues={onOpenIssues} />,
    INTEGRATIONS: <SentinelIntegrationsCard onOpenIssues={onOpenIssues} />,
    CHAOS_ENGINEERING: <SentinelChaosCard onOpenIssues={onOpenIssues} />,
  };

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Estado por componente</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {SENTINEL_COMPONENTS.map((c) => (
          <SentinelComponentRow key={c.code} name={c.name} summary={summaries[c.code]}>
            {bodies[c.code]}
          </SentinelComponentRow>
        ))}
      </CardContent>
    </Card>
  );
}
