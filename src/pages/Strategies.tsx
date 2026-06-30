import { useState } from "react";
import { Loader2, AlertCircle, Lightbulb, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FilterChips } from "@/components/ui/FilterChips";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useStrategiesList, useGenerateStrategy } from "@/hooks/useStrategies";
import { useUsedIdeas } from "@/hooks/useUsedIdeas";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import { IdeaUsageCard } from "@/components/strategies/IdeaUsageCard";
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
  used: "Aún no has usado ideas de tus estrategias. Usá la flecha de una idea y aparecerá acá.",
  archived: "Las estrategias que archives aparecerán acá.",
};

export default function Strategies() {
  const [estado, setEstado] = useState<Estado>("active");
  const { activeBusinessId, isReady } = useActiveBusiness();
  const list = useStrategiesList(estado);
  const usedIdeas = useUsedIdeas(activeBusinessId);          // Usadas = ideas sueltas (fuente distinta)
  const generate = useGenerateStrategy();
  const [packOpen, setPackOpen] = useState(false);
  useTrackOnMount("feature_open", { feature: "strategies" });

  // Usadas usa una fuente distinta (ideas sueltas) · Activas/Archivadas siguen con estrategias.
  const isUsed = estado === "used";
  const items = (list.data?.items ?? []).filter((s) => s.client_id === activeBusinessId);
  const ideas = usedIdeas.data ?? [];
  // Activas (C.1): idx de ideas usadas por estrategia → contador "quedan" + ocultar usadas del modal.
  const usedIdxByStrategy: Record<string, number[]> = {};
  ideas.forEach((i) => { (usedIdxByStrategy[i.strategy_id] ??= []).push(i.idea_idx); });
  const loading = isUsed ? usedIdeas.isLoading : list.isLoading;
  const isError = isUsed ? usedIdeas.isError : list.isError;
  const empty = isUsed ? ideas.length === 0 : items.length === 0;

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

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : isError ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="text-sm font-medium">No se pudieron cargar las estrategias</p>
          <Button size="sm" variant="outline" onClick={() => (isUsed ? usedIdeas.refetch() : list.refetch())}>Reintentar</Button>
        </CardContent></Card>
      ) : empty ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <Lightbulb className="h-10 w-10 text-muted-foreground/30" />
          <p className="text-sm font-medium">{isUsed ? "Todavía no hay ideas usadas" : "Todavía no hay estrategias"}</p>
          <p className="text-xs text-muted-foreground">{EMPTY[estado]}</p>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {isUsed
            ? ideas.map((idea) => <IdeaUsageCard key={idea.id} idea={idea} />)
            : items.map((s) => <StrategyCard key={s.id} strategy={s} variant={estado}
                usedCount={(usedIdxByStrategy[s.id] ?? []).length} usedIdxs={usedIdxByStrategy[s.id] ?? []} />)}
        </div>
      )}

      <PackOfStrategiesModal open={packOpen} onClose={() => setPackOpen(false)} />
    </div>
  );
}
