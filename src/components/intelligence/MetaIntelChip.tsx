import { Instagram } from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { useMetaChip } from "@/hooks/useMetaChip";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { IntelMetricGrid, IntelMetricGridSkeleton } from "./IntelMetricGrid";

// Centro de Inteligencia · chip Meta con datos REALES (solo CONSUMO · cero mocks).
// El connect vive en UN solo lugar (Cuentas Sociales) → acá, sin métricas, se apunta ahí.
export function MetaIntelChip() {
  const { data, isLoading, isError, error } = useMetaChip();
  const { activeBusinessId } = useActiveBusiness();

  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="flex flex-col items-center gap-5 py-10">
        <div className="flex flex-col items-center gap-3 text-center">
          <Instagram className="h-12 w-12 text-amber-500" />
          <p className="text-base font-medium text-foreground">Meta · Instagram y Facebook</p>
        </div>

        {isLoading && <div className="w-full"><IntelMetricGridSkeleton /></div>}

        {isError && (
          <p className="text-center text-sm text-muted-foreground font-body">
            {error.message || "No pudimos leer tus métricas de Meta ahora."}
          </p>
        )}

        {data && data.connected && (
          <div className="w-full">
            <IntelMetricGrid
              cells={[
                { label: "Seguidores", value: data.metrics?.followers },
                { label: "Engagement", value: data.metrics?.engagement },
                { label: "Alcance", value: data.metrics?.reach },
              ]}
            />
            {!data.metrics && data.message && (
              <p className="mt-3 text-center text-xs text-muted-foreground/70 font-body">{data.message}</p>
            )}
          </div>
        )}

        {data && !data.connected && (
          <div className="flex flex-col items-center gap-2 text-center">
            <p className="text-sm text-muted-foreground font-body">
              {data.message ?? "Conectá Meta para ver tus métricas reales."}
            </p>
            {activeBusinessId && (
              <Link to={`/clients/${activeBusinessId}`} className="text-sm text-primary hover:underline">
                Conectá tus cuentas en Cuentas Sociales →
              </Link>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
