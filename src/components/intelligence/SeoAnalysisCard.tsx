import { CheckCircle2, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SeoHeadingList } from "./SeoHeadingList";
import type { WebAnalysis } from "@/hooks/useWebAnalysis";

interface SeoAnalysisCardProps {
  data: WebAnalysis;
  onReanalyze: () => void;
  isReanalyzing: boolean;
}

function whenLabel(at: string | null): string {
  return at ? `Datos de ${new Date(at).toLocaleString()}` : "Sin fecha de análisis";
}

export function SeoAnalysisCard({ data, onReanalyze, isReanalyzing }: SeoAnalysisCardProps) {
  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="space-y-5 py-6">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground font-body">{whenLabel(data.generated_at)}</p>
          <Button size="sm" variant="outline" onClick={onReanalyze} disabled={isReanalyzing}>
            <RefreshCw className={isReanalyzing ? "animate-spin" : ""} />
            {isReanalyzing ? "Analizando…" : "Actualizar"}
          </Button>
        </div>

        <div className="flex items-end gap-3">
          <span className="text-5xl font-display font-bold text-amber-500">{data.score}</span>
          <span className="pb-1 text-sm text-muted-foreground font-body">/ 100 · Completitud SEO básica</span>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Keywords detectadas</p>
          {data.keywords.length === 0 ? (
            <p className="text-sm text-muted-foreground/60 font-body">Sin keywords detectadas</p>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {data.keywords.map((k, i) => (
                <Badge key={`kw-${i}`} variant="secondary">{k}</Badge>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-3">
          {(["H1", "H2", "H3"] as const).map((lvl) => (
            <SeoHeadingList key={lvl} label={lvl} items={data[lvl.toLowerCase() as "h1" | "h2" | "h3"]} />
          ))}
        </div>

        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Meta description</p>
          <p className="text-sm text-foreground font-body">
            {data.meta_description || <span className="text-muted-foreground/60">Sin meta description</span>}
          </p>
        </div>

        {data.recommendations.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Recomendaciones</p>
            <ul className="space-y-1">
              {data.recommendations.map((r, i) => (
                <li key={`rec-${i}`} className="flex items-start gap-2 text-sm text-foreground font-body">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
