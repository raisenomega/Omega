import { useState } from "react";
import { Loader2, AlertCircle, Lightbulb, ChevronDown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useStrategiesList, useGenerateStrategy } from "@/hooks/useStrategies";
import { StrategyCard } from "@/components/strategies/StrategyCard";

export default function Strategies() {
  const active = useStrategiesList("active");
  const archived = useStrategiesList("archived");
  const generate = useGenerateStrategy();
  const [histOpen, setHistOpen] = useState(false);
  useTrackOnMount("feature_open", { feature: "strategies" });

  const items = active.data?.items ?? [];
  const past = archived.data?.items ?? [];

  return (
    <div className="container mx-auto max-w-5xl px-4 py-6 space-y-4">
      <header className="flex items-start justify-between gap-3 flex-wrap">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold flex items-center gap-2"><Lightbulb className="h-6 w-6" /> Estrategias</h1>
          <p className="text-sm text-muted-foreground">
            ARIA prepara estrategias con tu contexto y las tendencias. Usalas, agendalas o pedí ajustes.
          </p>
        </div>
        <Button onClick={() => generate.mutate()} disabled={generate.isPending} className="gap-1">
          {generate.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Lightbulb className="h-4 w-4" />}
          Generar estrategia
        </Button>
      </header>

      {active.isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : active.isError ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="text-sm font-medium">No se pudieron cargar las estrategias</p>
          <Button size="sm" variant="outline" onClick={() => active.refetch()}>Reintentar</Button>
        </CardContent></Card>
      ) : items.length === 0 ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <Lightbulb className="h-10 w-10 text-muted-foreground/30" />
          <p className="text-sm font-medium">Todavía no hay estrategias</p>
          <p className="text-xs text-muted-foreground">Tocá "Generar estrategia" y ARIA preparará una con tu contexto.</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map((s) => <StrategyCard key={s.id} strategy={s} />)}
        </div>
      )}

      {past.length > 0 && (
        <Collapsible open={histOpen} onOpenChange={setHistOpen} className="pt-2">
          <CollapsibleTrigger className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground">
            <ChevronDown className={`h-3.5 w-3.5 transition-transform ${histOpen ? "" : "-rotate-90"}`} />
            Historial ({past.length})
          </CollapsibleTrigger>
          <CollapsibleContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-3">
            {past.map((s) => <StrategyCard key={s.id} strategy={s} archived />)}
          </CollapsibleContent>
        </Collapsible>
      )}
    </div>
  );
}
