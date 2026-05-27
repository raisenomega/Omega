import { LineChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useGoogleChip } from "@/hooks/useGoogleChip";
import { useGoogleConnect } from "@/hooks/useGoogleOAuth";
import { IntelMetricGrid, IntelMetricGridSkeleton } from "./IntelMetricGrid";

// Centro de Inteligencia Fase 2 · chip Google con datos REALES (GA4 + Search Console).
// connected + metrics → grilla real. connected=false → CTA "Conectá Google" (cero mocks).
export function GoogleIntelChip() {
  const { data, isLoading, isError, error } = useGoogleChip();
  const connect = useGoogleConnect();

  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="flex flex-col items-center gap-5 py-10">
        <div className="flex flex-col items-center gap-3 text-center">
          <LineChart className="h-12 w-12 text-amber-500" />
          <p className="text-base font-medium text-foreground">Google · Analytics y Search Console</p>
        </div>

        {isLoading && (
          <div className="w-full">
            <IntelMetricGridSkeleton />
          </div>
        )}

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
              <p className="mt-3 text-center text-xs text-muted-foreground/70 font-body">
                {data.message}
              </p>
            )}
          </div>
        )}

        {data && !data.connected && (
          <div className="flex flex-col items-center gap-3 text-center">
            <p className="text-sm text-muted-foreground font-body">
              {data.message ?? "Conectá Google para ver tus métricas reales."}
            </p>
            <Button
              onClick={() => connect.mutate()}
              disabled={connect.isPending}
              className="bg-amber-500/90 text-black hover:bg-amber-500"
            >
              Conectar Google Analytics
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
