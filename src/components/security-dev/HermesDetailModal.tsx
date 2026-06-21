import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown, MessageSquare, ExternalLink } from "lucide-react";
import { useHermesDetail, type HermesIncident } from "@/hooks/useHermesDetail";
import { useSecurityDev } from "@/contexts/SecurityDevContext";
import { integrationLabel, integrationUrl, statusInfo, effectiveStatus } from "./hermes-labels";
import { fmtDateTime, relativeAgo } from "./parts";

// Drill-down de una integración (espejo de GuardianDetailModal): ventanas de fallo + timeline + puente a
// Dev Chat con el contexto del fallo precargado (reusa SecurityDevContext · sin acciones de remediación).
function buildFixPrompt(integration: string, inc: HermesIncident): string {
  const url = integrationUrl(integration);
  return [`HERMES · ${integrationLabel(integration)} (${integration}) en fallo.`,
    `Último error: ${inc.detail ?? "—"}`,
    `En fallo desde: ${fmtDateTime(inc.started_at)} · último fallo: ${fmtDateTime(inc.last_failure_at)}`,
    url ? `Consola: ${url}` : "", "Diagnosticá la causa raíz y proponé el fix."].filter(Boolean).join("\n");
}

export function HermesDetailModal({ integration, onClose }: { integration: string; onClose: () => void }) {
  const { data, isLoading } = useHermesDetail(integration);
  const { setPendingFixPrompt, setActiveTab } = useSecurityDev();
  const [timelineOpen, setTimelineOpen] = useState(false);
  const incidents = data?.incidents ?? [];
  const url = integrationUrl(integration);

  const resolver = () => {
    const target = incidents.find((i) => i.recovered_at === null) ?? incidents[0];
    if (!target) return;
    setPendingFixPrompt(buildFixPrompt(integration, target));
    setActiveTab("chat");
  };

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="flex max-h-[90vh] max-w-lg flex-col">
        <DialogHeader><DialogTitle className="text-sm">{integrationLabel(integration)}</DialogTitle></DialogHeader>
        {isLoading || !data ? (
          <Skeleton className="h-48 w-full" />
        ) : (
          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto text-xs">
            {incidents.length === 0 ? (
              <p className="text-muted-foreground">
                {data.timeline.length === 0 ? "Sin uso registrado aún." : "Sin incidentes · todo en orden."}
              </p>
            ) : (
              <div>
                <p className="font-medium">Ventanas de fallo ({incidents.length})</p>
                {incidents.map((i, k) => (
                  <div key={k} className="mt-1 rounded border border-border/40 p-2">
                    <p className="text-[10px]">
                      <Badge variant="outline" className={i.recovered_at ? "" : "border-red-500/40 text-red-500"}>
                        {i.recovered_at ? "Recuperado" : "En curso"}
                      </Badge>{" "}
                      {fmtDateTime(i.started_at)} → {i.recovered_at ? fmtDateTime(i.recovered_at) : "—"}
                    </p>
                    <p className="font-mono text-[10px] text-muted-foreground">{i.detail ?? "—"}</p>
                  </div>
                ))}
              </div>
            )}
            <Collapsible open={timelineOpen} onOpenChange={setTimelineOpen}>
              <CollapsibleTrigger asChild>
                <button type="button" className="flex w-full items-center gap-2 hover:opacity-80">
                  <span className="font-medium">Historial ({data.timeline.length})</span>
                  <ChevronDown className={`h-3.5 w-3.5 shrink-0 transition-transform ${timelineOpen ? "" : "-rotate-90"}`} />
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                {data.timeline.map((t, k) => (
                  <div key={k} className="flex justify-between gap-2 border-b border-border/40 py-0.5 text-[10px]">
                    <span className="text-muted-foreground">{relativeAgo(t.created_at)}</span>
                    <span>{statusInfo(effectiveStatus({ integration, status: t.status, last_use: t.last_use })).label}</span>
                    <span className="truncate font-mono text-muted-foreground">{t.detail ?? ""}</span>
                  </div>
                ))}
              </CollapsibleContent>
            </Collapsible>
          </div>
        )}
        <div className="flex items-center gap-2 border-t border-border/40 pt-2">
          {url && (
            <a href={url} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center gap-1 text-xs text-primary hover:underline">
              Abrir consola <ExternalLink className="h-3 w-3" />
            </a>
          )}
          {incidents.length > 0 && (
            <Button size="sm" variant="outline" className="ml-auto" onClick={resolver}>
              <MessageSquare className="h-4 w-4" /><span className="ml-2">Resolver en Dev Chat →</span>
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
