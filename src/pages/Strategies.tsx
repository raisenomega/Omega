import { useState } from "react";
import { Loader2, Lightbulb, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FilterChips } from "@/components/ui/FilterChips";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useStrategiesList, useGenerateStrategy } from "@/hooks/useStrategies";
import { useUsedIdeas } from "@/hooks/useUsedIdeas";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import { IdeaUsageCard } from "@/components/strategies/IdeaUsageCard";
import { StrategiesGrid } from "@/components/strategies/StrategiesGrid";
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
  archived: "Las ideas que archives desde Usadas aparecerán acá.",
};

export default function Strategies() {
  const [estado, setEstado] = useState<Estado>("active");
  const { activeBusinessId, isReady } = useActiveBusiness();
  const list = useStrategiesList(estado);
  const usedIdeas = useUsedIdeas(activeBusinessId, false);    // Usadas + contador de Activas
  const archivedIdeas = useUsedIdeas(activeBusinessId, true); // Archivadas (ideas archivadas · C.2)
  const generate = useGenerateStrategy();
  const [packOpen, setPackOpen] = useState(false);
  useTrackOnMount("feature_open", { feature: "strategies" });

  // Activas = estrategias (StrategyCard) · Usadas/Archivadas = ideas sueltas (IdeaUsageCard · C.2).
  const isIdeaChip = estado !== "active";
  const items = (list.data?.items ?? []).filter((s) => s.client_id === activeBusinessId);
  const ideaQuery = estado === "archived" ? archivedIdeas : usedIdeas;
  const viewIdeas = ideaQuery.data ?? [];
  // Activas (C.1): idx de ideas usadas (NO archivadas) por estrategia → contador "quedan" + ocultar usadas del modal.
  const usedIdxByStrategy: Record<string, number[]> = {};
  (usedIdeas.data ?? []).forEach((i) => { (usedIdxByStrategy[i.strategy_id] ??= []).push(i.idea_idx); });
  const loading = isIdeaChip ? ideaQuery.isLoading : list.isLoading;
  const isError = isIdeaChip ? ideaQuery.isError : list.isError;
  const empty = isIdeaChip ? viewIdeas.length === 0 : items.length === 0;

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

      <StrategiesGrid
        loading={loading} isError={isError} empty={empty}
        emptyTitle={isIdeaChip ? "Todavía no hay ideas acá" : "Todavía no hay estrategias"}
        emptyMsg={EMPTY[estado]}
        onRetry={() => (isIdeaChip ? ideaQuery.refetch() : list.refetch())}
      >
        {isIdeaChip
          ? viewIdeas.map((idea) => <IdeaUsageCard key={idea.id} idea={idea} archived={estado === "archived"} />)
          : items.map((s) => <StrategyCard key={s.id} strategy={s} variant={estado}
              usedCount={(usedIdxByStrategy[s.id] ?? []).length} usedIdxs={usedIdxByStrategy[s.id] ?? []} />)}
      </StrategiesGrid>

      <PackOfStrategiesModal open={packOpen} onClose={() => setPackOpen(false)} />
    </div>
  );
}
