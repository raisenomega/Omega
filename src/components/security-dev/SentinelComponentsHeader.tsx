import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SENTINEL_COMPONENTS } from "@/lib/sentinel_components_registry";
import { SentinelComponentCard } from "./SentinelComponentCard";

// Catálogo "Componentes monitoreados" · los 10 componentes del registry como cards (qué vigila + frecuencia).
// AGENT_CHECKS se deriva del registry (fuente única) · lo consume SentinelAgentCard para el detalle per-agente.
export const AGENT_CHECKS: Record<string, string> = Object.fromEntries(
  SENTINEL_COMPONENTS.filter((c) => c.sourceTable === "sentinel_scans").map((c) => [c.code, c.whatItChecks]),
);

export function SentinelComponentsHeader() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Componentes monitoreados</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
          {SENTINEL_COMPONENTS.map((c) => (
            <SentinelComponentCard key={c.code} meta={c} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
