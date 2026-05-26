import { Globe, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useWebAnalysis } from "@/hooks/useWebAnalysis";
import { SeoAnalysisCard } from "./SeoAnalysisCard";
import { SeoFase2Lock } from "./SeoFase2Lock";

interface SeoChipProps {
  clientId: string;
}

export function SeoChip({ clientId }: SeoChipProps) {
  const { query, reanalyze, isReanalyzing } = useWebAnalysis(clientId);

  if (query.isLoading) {
    return (
      <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
        <CardContent className="space-y-3 py-6">
          <Skeleton className="h-12 w-32" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-4 w-1/2" />
        </CardContent>
      </Card>
    );
  }

  if (query.data && !query.data.analyzed) {
    return (
      <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center gap-3 py-14">
          <Globe className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground font-body">
            {query.data.message ?? "Este cliente no tiene sitio web configurado"}
          </p>
          <Button size="sm" variant="outline" onClick={() => reanalyze()} disabled={isReanalyzing}>
            <RefreshCw className={isReanalyzing ? "animate-spin" : ""} />
            {isReanalyzing ? "Analizando…" : "Analizar mi sitio"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {query.data && (
        <SeoAnalysisCard data={query.data} onReanalyze={() => reanalyze()} isReanalyzing={isReanalyzing} />
      )}
      <SeoFase2Lock />
    </div>
  );
}
