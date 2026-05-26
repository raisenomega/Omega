import { Bot, CheckCircle2, RefreshCw } from "lucide-react";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { dataAgoLabel } from "@/lib/relative-time";
import { useGeoCheck, type GeoStatus } from "@/hooks/useGeoCheck";

interface GeoChipProps {
  clientId: string;
}

const STATUS: Record<GeoStatus, { label: string; variant: BadgeProps["variant"]; className: string }> = {
  appeared:     { label: "Aparecés",                variant: "outline", className: "border-emerald-500/40 text-emerald-400" },
  partial:      { label: "Mencionado parcialmente", variant: "outline", className: "border-amber-500/40 text-amber-400" },
  not_appeared: { label: "No aparecés",             variant: "outline", className: "border-red-500/40 text-red-400" },
  unknown:      { label: "Sin determinar",          variant: "outline", className: "border-border text-muted-foreground" },
};

export function GeoChip({ clientId }: GeoChipProps) {
  const { query, recheck, isRechecking } = useGeoCheck(clientId);

  if (query.isLoading) {
    return (
      <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
        <CardContent className="space-y-3 py-6">
          <Skeleton className="h-7 w-40" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>
    );
  }

  if (query.data && !query.data.analyzed) {
    return (
      <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center gap-3 py-14">
          <Bot className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground font-body text-center">
            {query.data.message ?? "Todavía no verificamos si aparecés en las respuestas de IA"}
          </p>
          <Button size="sm" variant="outline" onClick={() => recheck()} disabled={isRechecking}>
            <RefreshCw className={isRechecking ? "animate-spin" : ""} />
            {isRechecking ? "Verificando…" : "Verificar visibilidad en IA"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!query.data) return null;
  const data = query.data;
  const s = STATUS[data.status];

  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="space-y-5 py-6">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground font-body">{dataAgoLabel(data.generated_at)}</p>
          <Button size="sm" variant="outline" onClick={() => recheck()} disabled={isRechecking}>
            <RefreshCw className={isRechecking ? "animate-spin" : ""} />
            {isRechecking ? "Verificando…" : "Actualizar"}
          </Button>
        </div>

        <Badge variant={s.variant} className={s.className}>{s.label}</Badge>

        {data.summary && <p className="text-sm text-foreground font-body">{data.summary}</p>}

        {data.tips.length > 0 && (
          <ul className="space-y-1.5">
            {data.tips.map((t, i) => (
              <li key={`geo-tip-${i}`} className="flex items-start gap-2 text-sm text-foreground font-body">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span>{t}</span>
              </li>
            ))}
          </ul>
        )}

        {data.queries.length > 0 && (
          <p className="text-xs text-muted-foreground/70 font-body">
            Consultas usadas: {data.queries.join(" · ")}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
