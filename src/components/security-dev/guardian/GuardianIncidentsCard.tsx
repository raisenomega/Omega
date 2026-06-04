import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown } from "lucide-react";
import { useGuardianIncidents } from "@/hooks/useGuardian";
import { IssueChip, relativeAgo, SEV_CLS } from "../parts";
import type { OpenGuardianDetail } from "@/types/guardian";

const SEVERITIES = ["critical", "high", "medium", "low"];

export function GuardianIncidentsCard({ onOpenDetail }: { onOpenDetail?: (d: OpenGuardianDetail) => void }) {
  const [sev, setSev] = useState<string | undefined>();
  const [open, setOpen] = useState(false);
  const { data, isLoading, isError } = useGuardianIncidents(undefined, sev);
  const incidents = data?.incidents ?? [];
  const openCount = incidents.filter((i) => i.status === "open").length;
  return (
    <Card>
      <CardHeader className="py-3">
        <button type="button" onClick={() => setOpen((v) => !v)} className="flex w-full items-center gap-2 text-sm hover:opacity-80">
          <CardTitle className="text-sm">Incidentes de seguridad</CardTitle>
          <span className="text-[10px] text-muted-foreground">{incidents.length} · {openCount} abiertos</span>
          <ChevronDown className={`ml-auto h-4 w-4 transition-transform ${open ? "" : "-rotate-90"}`} />
        </button>
      </CardHeader>
      {open && (
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <IssueChip onClick={() => setSev(undefined)}>
              <Badge variant="outline" className={!sev ? "border-primary/40 text-primary" : "border-border/40 text-muted-foreground"}>todas</Badge>
            </IssueChip>
            {SEVERITIES.map((s) => (
              <IssueChip key={s} onClick={() => setSev(s)}>
                <Badge variant="outline" className={SEV_CLS[s] ?? SEV_CLS.low}>{s}</Badge>
              </IssueChip>
            ))}
          </div>
          {isLoading ? (
            <Skeleton className="h-20 w-full" />
          ) : isError ? (
            <p className="text-xs text-red-500">Error al cargar incidentes · reintentá.</p>
          ) : incidents.length === 0 ? (
            <p className="text-xs text-muted-foreground">Sin incidentes{sev ? ` ${sev}` : " abiertos"} · todo en orden.</p>
          ) : (
            <div className="space-y-0.5">
              {incidents.slice(0, 20).map((i) => (
                <button key={i.id} type="button" onClick={() => onOpenDetail?.({ kind: "incident", userId: i.user_id, incidentId: i.id })}
                  className="flex w-full items-center justify-between gap-2 border-b border-border/40 py-1 text-left text-[11px] hover:bg-muted/30">
                  <span className="w-16 shrink-0 text-muted-foreground">{relativeAgo(i.detected_at)}</span>
                  <span className="flex-1 font-medium">{i.incident_type}</span>
                  <Badge variant="outline" className={SEV_CLS[i.severity] ?? SEV_CLS.low}>{i.severity}</Badge>
                  <span className="w-24 text-right text-muted-foreground">{i.status}</span>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
