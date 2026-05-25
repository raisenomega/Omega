import { ShieldCheck, AlertTriangle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useSentinelStatus } from "@/hooks/useSentinelStatus";

// SENTINEL 4B-5 · salud del sistema (solo owner/superadmin · dato real · empty state honesto P1)
const STATUS_LABEL: Record<string, string> = {
  presidencial: "Presidencial", warning: "Atención", critical: "Crítico",
};

function fmt(at: string): string {
  const d = new Date(at);
  return isNaN(d.getTime()) ? at : d.toLocaleString("es-AR", { dateStyle: "short", timeStyle: "short" });
}

export function SentinelDashboardCard() {
  const { data, isLoading, isError } = useSentinelStatus();
  const blocked = data?.deploy_decision === "BLOCK";

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm">SENTINEL · Salud del sistema</CardTitle>
        {data && (blocked
          ? <AlertTriangle className="h-4 w-4 text-red-500" />
          : <ShieldCheck className="h-4 w-4 text-emerald-500" />)}
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="flex items-center gap-2 text-xs text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" />Cargando…</div>
        ) : isError || !data ? (
          <p className="text-xs text-muted-foreground">SENTINEL aún no ha escaneado · sin datos.</p>
        ) : (
          <>
            <div className="flex items-end gap-3">
              <span className="text-3xl font-bold tabular-nums">{data.security_score}<span className="text-sm text-muted-foreground">/100</span></span>
              <Badge variant={blocked ? "destructive" : "secondary"} className="text-[10px] mb-1">{STATUS_LABEL[data.status] ?? data.status}</Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Deploy: <span className={blocked ? "text-red-500 font-medium" : "text-emerald-600 font-medium"}>{data.deploy_decision}</span>
              {data.active_issues.length > 0 && ` · ${data.active_issues.length} issue(s) activos`}
            </p>
            {data.last_scan && <p className="text-[10px] text-muted-foreground">Último scan: {fmt(data.last_scan)}</p>}
          </>
        )}
      </CardContent>
    </Card>
  );
}
