import { useState } from "react";
import { Brain } from "lucide-react";
import { useProAccess } from "@/hooks/useProAccess";
import { IntelligenceChips } from "@/components/intelligence/IntelligenceChips";
import { ResumenChip } from "@/components/intelligence/ResumenChip";
import { SeoChip } from "@/components/intelligence/SeoChip";
import { GeoChip } from "@/components/intelligence/GeoChip";
import { AeoChip } from "@/components/intelligence/AeoChip";
import { MetaIntelChip } from "@/components/intelligence/MetaIntelChip";
import { GoogleIntelChip } from "@/components/intelligence/GoogleIntelChip";
import { IntelligenceLoading, IntelligencePlanGate } from "@/components/intelligence/IntelligenceGate";
import { type ChipId } from "@/components/intelligence/_chips";

export default function IntelligencePage() {
  const { clientId, loading, hasPro } = useProAccess();
  const [active, setActive] = useState<ChipId>("resumen");

  if (loading) return <IntelligenceLoading />;
  if (!hasPro) return <IntelligencePlanGate clientId={clientId} />;

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

      {active === "resumen" && <ResumenChip clientId={clientId ?? ""} />}
      {active === "seo" && <SeoChip clientId={clientId ?? ""} />}
      {active === "geo" && <GeoChip clientId={clientId ?? ""} />}
      {active === "aeo" && <AeoChip clientId={clientId ?? ""} />}
      {active === "meta" && <MetaIntelChip />}
      {active === "google" && <GoogleIntelChip />}
    </div>
  );
}
