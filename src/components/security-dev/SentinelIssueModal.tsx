import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useSentinelHistory } from "@/hooks/useSecurityDevData";
import { useSentinelIssueAction, type IssueActionPayload } from "@/hooks/useSentinelIssueAction";
import { groupSentinelRuns } from "./parts";

interface Props {
  open: boolean;
  onClose: () => void;
  scope: "aggregate" | "agent";
  severity?: string;   // CRITICAL/HIGH/MEDIUM (scope aggregate)
  agentCode?: string;  // scope agent
}

// Lista issues del último run (/sentinel/history per-agente · el agregado no tiene detalle).
export function SentinelIssueModal({ open, onClose, scope, severity, agentCode }: Props) {
  const { data, isLoading } = useSentinelHistory();
  const { ignoreMutation, fixMutation } = useSentinelIssueAction();
  const latest = groupSentinelRuns(data?.scans ?? [])[0]?.scans ?? [];
  const rows = latest
    .filter((s) => (scope === "agent" ? s.agent_code === agentCode : true))
    .flatMap((s) => s.issues.map((it) => ({ it, agent_code: s.agent_code, scan_id: s.id })))
    .filter(({ it }) => (scope === "aggregate" && severity ? it.severity === severity : true));

  const payload = (r: (typeof rows)[number]): IssueActionPayload => ({
    agent_code: r.agent_code, severity: r.it.severity, type: r.it.type, message: r.it.message, scan_id: r.scan_id,
  });
  const busy = ignoreMutation.isPending || fixMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-sm">
            Issues {scope === "agent" ? `· ${agentCode}` : severity ? `· ${severity}` : ""}
          </DialogTitle>
        </DialogHeader>
        {isLoading ? (
          <Skeleton className="h-32 w-full" />
        ) : rows.length === 0 ? (
          <p className="text-sm text-muted-foreground">Sin issues de esta severidad.</p>
        ) : (
          <div className="max-h-[60vh] space-y-2 overflow-y-auto">
            {rows.map((r, i) => {
              const ignored = (r.it.previous_actions ?? []).some((a) => a.action === "ignored");
              return (
                <div key={i} className="space-y-1 rounded-lg border border-border/40 p-3 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium">{r.it.severity} · {r.it.type}</span>
                    {ignored && (
                      <Badge variant="outline" className="border-border/40 text-muted-foreground">ignorado previamente</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{r.it.message}</p>
                  <p className="text-[10px] text-muted-foreground">{r.agent_code}</p>
                  <div className="flex gap-2 pt-1">
                    <Button size="sm" variant="outline" disabled={busy} onClick={() => ignoreMutation.mutate(payload(r))}>Ignorar</Button>
                    <Button size="sm" disabled={busy} onClick={() => fixMutation.mutate(payload(r))}>Fix</Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
