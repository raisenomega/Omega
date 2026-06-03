import { useQuery } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useSentinelIssueAction, type IssueActionPayload } from "@/hooks/useSentinelIssueAction";
import { loadIssuesBySource, type NormalizedIssue, type OpenIssuesParams } from "@/lib/sentinel_issue_loaders";
import { buildFixPrompt } from "@/lib/sentinel_fix_prompt_builders";

interface Props extends OpenIssuesParams { open: boolean; onClose: () => void; }

// Modal universal · lee issues de cualquier source_type vía loadIssuesBySource (mismo render UI).
// sentinel_scan = comportamiento legacy idéntico (incluye badge "ignorado previamente").
export function SentinelIssueModal({ open, onClose, sourceType, sourceId, severity, agentCode, scopeLabel }: Props) {
  const { ignoreMutation, fixMutation } = useSentinelIssueAction();
  const { data, isLoading } = useQuery({
    queryKey: ["sentinel-issues", sourceType, sourceId ?? null, severity ?? null, agentCode ?? null],
    queryFn: () => loadIssuesBySource({ sourceType, sourceId, severity, agentCode }),
  });
  const rows = data ?? [];
  const payload = (i: NormalizedIssue, withPrompt: boolean): IssueActionPayload => ({
    agent_code: i.agentCode ?? "global", severity: i.severity, type: i.type, message: i.message,
    scan_id: i.sourceId, source_type: i.sourceType, source_id: i.sourceId,
    ...(withPrompt ? { dispatch_prompt: buildFixPrompt(i) } : {}),
  });
  const busy = ignoreMutation.isPending || fixMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-sm">Issues{scopeLabel ? ` · ${scopeLabel}` : ""}</DialogTitle>
        </DialogHeader>
        {isLoading ? (
          <Skeleton className="h-32 w-full" />
        ) : rows.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {scopeLabel ? `${scopeLabel} · sin issues abiertos` : "Sin issues abiertos para esta selección"} · componente sano, nada que accionar.
          </p>
        ) : (
          <div className="max-h-[60vh] space-y-2 overflow-y-auto">
            {rows.map((i) => {
              const ignored = i.previousActions.some((a) => a.action === "ignored");
              return (
                <div key={i.key} className="space-y-1 rounded-lg border border-border/40 p-3 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium">{i.severity} · {i.type}</span>
                    {ignored && (
                      <Badge variant="outline" className="border-border/40 text-muted-foreground">ignorado previamente</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{i.message}</p>
                  {i.agentCode && <p className="text-[10px] text-muted-foreground">{i.agentCode}</p>}
                  <div className="flex gap-2 pt-1">
                    <Button size="sm" variant="outline" disabled={busy} onClick={() => ignoreMutation.mutate(payload(i, false))}>Ignorar</Button>
                    <Button size="sm" disabled={busy} onClick={() => fixMutation.mutate(payload(i, true))}>Fix</Button>
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
