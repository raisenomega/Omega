import { useState } from "react";
import { Loader2, AlertCircle, Lightbulb, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FilterChips } from "@/components/ui/FilterChips";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useStrategiesList, useGenerateStrategy } from "@/hooks/useStrategies";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import { PackOfStrategiesModal } from "@/components/strategies/PackOfStrategiesModal";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";

// Subtítulo · frase fija y corta (no se compone por cadencia · "según tu plan" lo cubre de forma
// honesta para cualquier plan, incluido Adopción que no recibe automáticas).
const SUBTITLE = "ARIA prepara estrategias con tu contexto y las tendencias del momento y recibes automáticamente según tu plan.";

type Estado = "active" | "used" | "archived";
const CHIPS = [
  { id: "active", label: "Activas" },
  { id: "used", label: "Usadas" },
  { id: "archived", label: "Archivadas" },
];
const EMPTY: Record<Estado, string> = {
  active: 'Tocá "Generar estrategia" y ARIA preparará una con tu contexto.',
  used: "Las estrategias que uses aparecerán acá · podés volver a usarlas.",
  archived: "Las estrategias que archives aparecerán acá.",
};

export default function Strategies() {
  const [estado, setEstado] = useState<Estado>("active");
  const list = useStrategiesList(estado);
  const generate = useGenerateStrategy();
  const [packOpen, setPackOpen] = useState(false);
  useTrackOnMount("feature_open", { feature: "strategies" });
  const { activeBusinessId, isReady } = useActiveBusiness();

  const items = (list.data?.items ?? []).filter((s) => s.client_id === activeBusinessId);

  if (!isReady) return null;
  if (!activeBusinessId) return <EmptyState feature="Estrategias" />;

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-3">
        <div className="space-y-1 min-w-0">
          <h1 className="text-2xl font-display font-bold tracking-tight">Estrategias</h1>
          <p className="text-sm text-muted-foreground">{SUBTITLE}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0 whitespace-nowrap">
          <Button onClick={() => generate.mutate(activeBusinessId ?? undefined)} disabled={generate.isPending} className="gap-1">
            {generate.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Lightbulb className="h-4 w-4" />}
            Generar estrategia
          </Button>
          <Button variant="outline" onClick={() => setPackOpen(true)} className="gap-1">
            <Sparkles className="h-4 w-4" /> Pack de Estrategias
          </Button>
        </div>
      </header>

      <FilterChips items={CHIPS} active={estado} onSelect={(id) => setEstado(id as Estado)} />

      {list.isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : list.isError ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="text-sm font-medium">No se pudieron cargar las estrategias</p>
          <Button size="sm" variant="outline" onClick={() => list.refetch()}>Reintentar</Button>
        </CardContent></Card>
      ) : items.length === 0 ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <Lightbulb className="h-10 w-10 text-muted-foreground/30" />
          <p className="text-sm font-medium">Todavía no hay estrategias</p>
          <p className="text-xs text-muted-foreground">{EMPTY[estado]}</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {items.map((s) => <StrategyCard key={s.id} strategy={s} variant={estado} />)}
        </div>
      )}

      <PackOfStrategiesModal open={packOpen} onClose={() => setPackOpen(false)} />
    </div>
  );
}
