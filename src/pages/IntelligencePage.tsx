import { useState } from "react";
import { Brain } from "lucide-react";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useClientPlanStatus } from "@/hooks/useClientPlanStatus";
import { IntelligenceChips } from "@/components/intelligence/IntelligenceChips";
import { ChipPlaceholder } from "@/components/intelligence/ChipPlaceholder";
import { IntelligenceLoading, IntelligencePlanGate } from "@/components/intelligence/IntelligenceGate";
import { type ChipId } from "@/components/intelligence/_chips";

const CHIP_LABELS: Record<ChipId, string> = {
  resumen: "Resumen General",
  seo:     "Posicionamiento SEO",
  geo:     "GEO · Search generativa",
  aeo:     "AEO · Answer Engine",
  meta:    "Meta · Rendimiento de anuncios",
  google:  "Google · Performance",
};

export default function IntelligencePage() {
  const { clientId, loading } = useMyPlanStatus();
  const plan = useClientPlanStatus(clientId ?? "");
  const [active, setActive] = useState<ChipId>("resumen");

  if (loading || plan.loading) return <IntelligenceLoading />;

  const isPro = plan.planCode === "pro" || plan.planCode === "enterprise";
  if (!isPro) return <IntelligencePlanGate clientId={clientId} />;

  return (
    <div className="container mx-auto max-w-5xl px-4 py-6 space-y-6">
      <header className="flex items-center gap-3">
        <Brain className="h-7 w-7 text-amber-500" />
        <div>
          <h1 className="text-2xl font-display font-bold tracking-tight">
            Centro de Inteligencia
          </h1>
          <p className="text-sm text-muted-foreground font-body">
            Tu presencia digital, analizada
          </p>
        </div>
      </header>

      <IntelligenceChips active={active} onSelect={setActive} />

      <ChipPlaceholder title={CHIP_LABELS[active]} />
    </div>
  );
}
