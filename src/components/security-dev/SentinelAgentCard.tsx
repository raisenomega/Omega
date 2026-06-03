import { Badge } from "@/components/ui/badge";
import { fmtDateTime } from "./parts";
import { AGENT_CHECKS } from "./SentinelComponentsHeader";
import type { SentinelScan } from "@/hooks/useSecurityDevData";

const STATUS_CLS: Record<string, string> = {
  pass: "bg-green-500/15 text-green-500 border-green-500/40",
  warning: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  fail: "bg-red-500/15 text-red-500 border-red-500/40",
  critical: "bg-red-500/15 text-red-500 border-red-500/40",
};

const fmtMs = (ms: number | null) => (ms == null ? "—" : ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`);

export function SentinelAgentCard({ scan, onOpenIssues }: { scan: SentinelScan; onOpenIssues: () => void }) {
  const cls = STATUS_CLS[scan.status] ?? "bg-muted/40 text-muted-foreground border-border/40";
  return (
    <div className="space-y-1 rounded-lg border border-border/40 p-3 text-sm">
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium">{scan.agent_code}</span>
        <Badge variant="outline" className={cls}>{scan.status}</Badge>
      </div>
      <p className="text-xs text-muted-foreground">{AGENT_CHECKS[scan.agent_code] ?? "—"}</p>
      <p className="text-xs text-muted-foreground">
        Score: {scan.security_score ?? "—"} · Decisión: {scan.deploy_decision ?? "—"} · Duración: {fmtMs(scan.scan_duration_ms)}
      </p>
      <p className="text-xs text-muted-foreground">{fmtDateTime(scan.created_at)} · origen: {scan.triggered_by ?? "—"}</p>
      <button onClick={onOpenIssues} className="w-full rounded text-left hover:bg-muted/40">
        {scan.issues.length === 0 ? (
          <span className="text-xs text-green-500">Sin issues encontrados ✅ · gestionar</span>
        ) : (
          <ul className="list-disc space-y-0.5 pl-4 text-xs text-muted-foreground">
            {scan.issues.map((it, i) => (
              <li key={i}><span className="font-medium">{it.severity}</span> · {it.type} · {it.message}</li>
            ))}
          </ul>
        )}
      </button>
    </div>
  );
}
