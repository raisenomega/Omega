import { useState } from "react";
import { useGuardianEvents, useGuardianIncidents, useGuardianWatchlist } from "@/hooks/useGuardian";
import { GuardianUserEventsCard } from "./guardian/GuardianUserEventsCard";
import { GuardianIncidentsCard } from "./guardian/GuardianIncidentsCard";
import { GuardianWatchlistCard } from "./guardian/GuardianWatchlistCard";
import { GuardianDetailModal } from "./guardian/GuardianDetailModal";
import type { OpenGuardianDetail } from "@/types/guardian";

// GUARDIAN · Seguridad Usuario/Sesión (4B-4) · panel owner-only paralelo a SENTINEL.
export function GuardianTab() {
  const [detail, setDetail] = useState<OpenGuardianDetail | null>(null);
  const events = useGuardianEvents().data?.events ?? [];
  const incidents = useGuardianIncidents().data?.incidents ?? [];
  const watch = useGuardianWatchlist(undefined, true).data?.watchlist ?? [];
  const openInc = incidents.filter((i) => i.status === "open").length;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-base font-semibold">GUARDIAN · Seguridad Usuario/Sesión</h2>
        <div className="mt-1 flex flex-wrap gap-4 text-xs text-muted-foreground">
          <span><span className="font-semibold text-foreground">{events.length}</span> eventos</span>
          <span><span className={`font-semibold ${openInc ? "text-amber-500" : "text-foreground"}`}>{openInc}</span> incidentes abiertos</span>
          <span><span className="font-semibold text-foreground">{watch.length}</span> IPs en watchlist activa</span>
        </div>
      </div>

      <GuardianUserEventsCard onOpenDetail={setDetail} />
      <GuardianIncidentsCard onOpenDetail={setDetail} />
      <GuardianWatchlistCard onOpenDetail={setDetail} />

      {detail && <GuardianDetailModal detail={detail} onClose={() => setDetail(null)} />}
    </div>
  );
}
