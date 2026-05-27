import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useSentinelData, type SentinelScore } from "@/hooks/useSecurityDevData";
import { scoreColor, fmtDateTime } from "./parts";

export function SentinelTab() {
  const { data, isLoading, error } = useSentinelData();

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  const err = (error as Error)?.message ?? data?.error;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;
  if (!data || data.count === 0)
    return <p className="text-sm text-muted-foreground">Sin corridas registradas aún. SENTINEL corre a las 7 AM.</p>;

  const latest = data.latest as SentinelScore;
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>Último scan</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-baseline gap-3">
            <span className={`text-5xl font-bold ${scoreColor(latest.score)}`}>{Math.round(latest.score)}</span>
            <span className="text-sm text-muted-foreground">/100 · {latest.verdict}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="bg-red-500/15 text-red-500 border-red-500/40">críticos {latest.issues_critical}</Badge>
            <Badge variant="outline" className="bg-orange-500/15 text-orange-500 border-orange-500/40">altos {latest.issues_high}</Badge>
            <Badge variant="outline" className="bg-amber-500/15 text-amber-500 border-amber-500/40">medios {latest.issues_medium}</Badge>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-sm">Últimas corridas</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {data.history.map((r) => (
            <div key={r.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-sm">
              <span className="text-muted-foreground">{fmtDateTime(r.calculated_at)}</span>
              <span className={`font-medium ${scoreColor(r.score)}`}>{Math.round(r.score)}</span>
              <span className="text-xs text-muted-foreground">{r.verdict}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
