import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown } from "lucide-react";
import { useGuardianEvents } from "@/hooks/useGuardian";
import { IssueChip, relativeAgo, scoreColor } from "../parts";
import type { OpenGuardianDetail } from "@/types/guardian";

const TYPES = ["login_success", "login_failed", "suspicious_activity", "new_device", "logout", "password_reset"];

export function GuardianUserEventsCard({ onOpenDetail }: { onOpenDetail?: (d: OpenGuardianDetail) => void }) {
  const [filter, setFilter] = useState<string | undefined>();
  const [open, setOpen] = useState(false);
  const { data, isLoading, isError } = useGuardianEvents(filter);
  const events = data?.events ?? [];
  const failed = events.filter((e) => e.event_type === "login_failed").length;
  return (
    <Card>
      <CardHeader className="py-3">
        <button type="button" onClick={() => setOpen((v) => !v)} className="flex w-full items-center gap-2 text-sm hover:opacity-80">
          <CardTitle className="text-sm">Eventos de seguridad</CardTitle>
          <span className="text-[10px] text-muted-foreground">{events.length} · {failed} login fallidos</span>
          <ChevronDown className={`ml-auto h-4 w-4 transition-transform ${open ? "" : "-rotate-90"}`} />
        </button>
      </CardHeader>
      {open && (
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <IssueChip onClick={() => setFilter(undefined)}>
              <Badge variant="outline" className={!filter ? "border-primary/40 text-primary" : "border-border/40 text-muted-foreground"}>todos</Badge>
            </IssueChip>
            {TYPES.map((t) => (
              <IssueChip key={t} onClick={() => setFilter(t)}>
                <Badge variant="outline" className={filter === t ? "border-primary/40 text-primary" : "border-border/40 text-muted-foreground"}>{t}</Badge>
              </IssueChip>
            ))}
          </div>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : isError ? (
            <p className="text-xs text-red-500">Error al cargar eventos · reintentá.</p>
          ) : events.length === 0 ? (
            <p className="text-xs text-muted-foreground">Sin eventos{filter ? ` de tipo ${filter}` : " en la ventana"}.</p>
          ) : (
            <div className="space-y-0.5">
              {events.slice(0, 20).map((e) => (
                <button key={e.id} type="button" onClick={() => onOpenDetail?.({ kind: "event", userId: e.user_id })}
                  className="flex w-full items-center justify-between gap-2 border-b border-border/40 py-1 text-left text-[11px] hover:bg-muted/30">
                  <span className="w-16 shrink-0 text-muted-foreground">{relativeAgo(e.created_at)}</span>
                  <span className="flex-1 font-medium">{e.event_type}</span>
                  <span className="font-mono text-muted-foreground">{e.ip_address ?? "—"}</span>
                  <span className="w-8 text-muted-foreground">{e.country ?? "—"}</span>
                  <span className={`w-8 text-right ${scoreColor(100 - e.risk_score)}`}>r{e.risk_score}</span>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
