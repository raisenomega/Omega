import { LineChart } from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { useGoogleChip } from "@/hooks/useGoogleChip";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { IntelMetricGrid, IntelMetricGridSkeleton } from "./IntelMetricGrid";

// Centro de Inteligencia · chip Google (GA4 + Search Console) · solo CONSUMO (cero mocks).
// El connect vive en UN solo lugar (Cuentas Sociales) → acá, sin métricas, se apunta ahí.
export function GoogleIntelChip() {
  const { data, isLoading, isError, error } = useGoogleChip();
  const { activeBusinessId } = useActiveBusiness();

  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="flex flex-col items-center gap-5 py-10">
        <div className="flex flex-col items-center gap-3 text-center">
          <LineChart className="h-12 w-12 text-amber-500" />
          <p className="text-base font-medium text-foreground">Google · Analytics y Search Console</p>
        </div>

        {isLoading && <div className="w-full"><IntelMetricGridSkeleton /></div>}

        {isError && (
          <p className="text-center text-sm text-muted-foreground font-body">
            {error.message || "No pudimos leer tus métricas de Google ahora."}
          </p>
        )}

        {data && data.connected && (
          <div className="w-full">
            <IntelMetricGrid
              cells={[
                { label: "Sesiones", value: data.metrics?.sessions },
                { label: "Clics", value: data.metrics?.clicks },
                { label: "Impresiones", value: data.metrics?.impressions },
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
              {data.message ?? "Conectá Google para ver tus métricas reales."}
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
