import { Globe, Search, Sparkles, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useWebAnalysis } from "@/hooks/useWebAnalysis";
import { useGeoCheck } from "@/hooks/useGeoCheck";
import { ResumenStatusRow } from "./ResumenStatusRow";
import { buildIntelligenceBrief, geoStatusLabel } from "./resumen-brief";

interface ResumenChipProps {
  clientId: string;
}

export function ResumenChip({ clientId }: ResumenChipProps) {
  const navigate = useNavigate();
  const { query: web } = useWebAnalysis(clientId);
  const { query: geo } = useGeoCheck(clientId);

  if (web.isLoading || geo.isLoading) {
    return <div className="space-y-3">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-16 w-full" />)}</div>;
  }

  const w = web.data;
  const g = geo.data;
  const analyzed = w?.analyzed ?? false;
  const topKeywords = w?.keywords.slice(0, 3) ?? [];

  const goToBrief = () => {
    const brief = buildIntelligenceBrief(w, g);
    navigate("/content-lab", { state: { brief } });
  };

  return (
    <div className="space-y-3">
      <ResumenStatusRow icon={<Globe className="h-5 w-5" />} label="Sitio web" muted={!analyzed}
        value={analyzed
          ? `Score ${w?.score}/100 · analizado ${w?.generated_at ? new Date(w.generated_at).toLocaleDateString() : "—"}`
          : "Sin analizar aún · analizá tu sitio primero"} />

      <ResumenStatusRow icon={<Search className="h-5 w-5" />} label="SEO · keywords detectadas" muted={!topKeywords.length}
        value={topKeywords.length ? topKeywords.join(" · ") : "Sin datos · analizá tu sitio primero"} />

      <ResumenStatusRow icon={<Sparkles className="h-5 w-5" />} label="GEO · ¿Aparecés en ChatGPT?" muted={!g?.analyzed}
        value={g?.analyzed ? geoStatusLabel(g.status) : "Sin verificar · corré el chequeo GEO"} />

      <Button onClick={goToBrief} disabled={!analyzed && !g?.analyzed}
        className="w-full bg-amber-500 text-black hover:bg-amber-500/90">
        Generar Brief para Content Lab
        <ArrowRight className="h-4 w-4" />
      </Button>
      {!analyzed && !g?.analyzed && (
        <p className="text-center text-xs text-muted-foreground/60 font-body">
          Analizá tu sitio o verificá tu visibilidad IA para generar un brief
        </p>
      )}
    </div>
  );
}
