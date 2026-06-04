import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuardianUserDetail } from "@/hooks/useGuardian";
import { fmtDateTime, relativeAgo, SEV_CLS } from "../parts";
import type { OpenGuardianDetail } from "@/types/guardian";

const tzOf = (geo: Record<string, unknown> | null): string => {
  const tz = geo?.timezone;
  return typeof tz === "string" ? tz : "tz —";
};

// Sub-A: detalle read-only con data real (email + último login geo/session/UA + historial + incidents).
// Sub-B agrega el footer con [false positive] / [tomar acción] / [Consultar con Claude].
export function GuardianDetailModal({ detail, onClose }: { detail: OpenGuardianDetail; onClose: () => void }) {
  const { data, isLoading } = useGuardianUserDetail(detail.userId ?? null);
  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-sm">Detalle {detail.kind === "watchlist" ? `· IP ${detail.ip}` : "· usuario"}</DialogTitle>
        </DialogHeader>
        {detail.kind === "watchlist" ? (
          <p className="text-xs text-muted-foreground">Entrada de watchlist · IP {detail.ip}.</p>
        ) : !detail.userId ? (
          <p className="text-xs text-muted-foreground">Evento sin usuario asociado.</p>
        ) : isLoading || !data ? (
          <Skeleton className="h-48 w-full" />
        ) : (
          <div className="max-h-[65vh] space-y-3 overflow-y-auto text-xs">
            <div>
              <p className="font-medium">{data.email ?? "(email no disponible)"}</p>
              <p className="text-[10px] text-muted-foreground">
                user {data.user_id.slice(0, 8)} · alta {data.account_created ? fmtDateTime(data.account_created) : "—"} · último acceso {data.last_sign_in ? fmtDateTime(data.last_sign_in) : "—"}
              </p>
            </div>
            {data.last_login && (
              <div className="rounded border border-border/40 p-2">
                <p className="font-medium">Último login</p>
                <p className="text-[10px] text-muted-foreground">{data.last_login.ip_address ?? "—"} · {data.last_login.country ?? "país —"} · {tzOf(data.last_login.geo)}</p>
                <p className="text-[10px] text-muted-foreground">session {data.last_login.session_id ?? "—"} · UA {(data.last_login.user_agent ?? "—").slice(0, 60)}</p>
              </div>
            )}
            {data.watchlist_matches.length > 0 && (
              <p className="text-[10px] text-amber-500">alerta · {data.watchlist_matches.length} IP(s) del usuario en watchlist</p>
            )}
            {data.open_incidents.length > 0 && (
              <div>
                <p className="font-medium">Incidentes abiertos ({data.open_incidents.length})</p>
                {data.open_incidents.map((i) => (
                  <p key={i.id} className="text-[10px] text-muted-foreground">· {i.incident_type} <Badge variant="outline" className={SEV_CLS[i.severity] ?? SEV_CLS.low}>{i.severity}</Badge></p>
                ))}
              </div>
            )}
            <div>
              <p className="font-medium">Historial ({data.history.length})</p>
              {data.history.map((e) => (
                <div key={e.id} className="flex justify-between gap-2 border-b border-border/40 py-0.5 text-[10px]">
                  <span className="text-muted-foreground">{relativeAgo(e.created_at)}</span>
                  <span>{e.event_type}</span>
                  <span className="font-mono text-muted-foreground">{e.ip_address ?? "—"}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
