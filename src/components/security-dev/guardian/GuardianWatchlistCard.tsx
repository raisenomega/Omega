import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown } from "lucide-react";
import { useGuardianWatchlist } from "@/hooks/useGuardian";
import { IssueChip, relativeAgo, fmtDateTime, LIST_CLS } from "../parts";
import type { OpenGuardianDetail } from "@/types/guardian";

const LIST_TYPES = ["block", "watch", "allow"];

export function GuardianWatchlistCard({ onOpenDetail }: { onOpenDetail?: (d: OpenGuardianDetail) => void }) {
  const [lt, setLt] = useState<string | undefined>();
  const [open, setOpen] = useState(false);
  const { data, isLoading } = useGuardianWatchlist(lt);
  const rows = data?.watchlist ?? [];
  const blocks = rows.filter((w) => w.list_type === "block").length;
  return (
    <Card>
      <CardHeader className="py-3">
        <button type="button" onClick={() => setOpen((v) => !v)} className="flex w-full items-center gap-2 text-sm hover:opacity-80">
          <CardTitle className="text-sm">IP Watchlist</CardTitle>
          <span className="text-[10px] text-muted-foreground">{rows.length} · {blocks} block</span>
          <ChevronDown className={`ml-auto h-4 w-4 transition-transform ${open ? "" : "-rotate-90"}`} />
        </button>
      </CardHeader>
      {open && (
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <IssueChip onClick={() => setLt(undefined)}>
              <Badge variant="outline" className={!lt ? "border-primary/40 text-primary" : "border-border/40 text-muted-foreground"}>todas</Badge>
            </IssueChip>
            {LIST_TYPES.map((t) => (
              <IssueChip key={t} onClick={() => setLt(t)}>
                <Badge variant="outline" className={LIST_CLS[t] ?? LIST_CLS.watch}>{t}</Badge>
              </IssueChip>
            ))}
          </div>
          {isLoading ? (
            <Skeleton className="h-20 w-full" />
          ) : rows.length === 0 ? (
            <p className="text-xs text-muted-foreground">IP Watchlist vacía{lt ? ` (${lt})` : ""} · se llena al detectar abuso.</p>
          ) : (
            <div className="space-y-0.5">
              {rows.slice(0, 20).map((w) => (
                <button key={w.id} type="button" onClick={() => onOpenDetail?.({ kind: "watchlist", ip: w.ip_address })}
                  className="flex w-full items-center justify-between gap-2 border-b border-border/40 py-1 text-left text-[11px] hover:bg-muted/30">
                  <span className="font-mono">{w.ip_address}</span>
                  <Badge variant="outline" className={LIST_CLS[w.list_type] ?? LIST_CLS.watch}>{w.list_type}</Badge>
                  <span className="max-w-[35%] flex-1 truncate text-muted-foreground">{w.reason ?? "—"}</span>
                  <span className="text-muted-foreground">{w.expires_at ? `exp ${fmtDateTime(w.expires_at)}` : "perm"}</span>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
