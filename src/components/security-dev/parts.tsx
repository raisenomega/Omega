// Primitivas compartidas de Security Dev (mantiene cada tab ≤75L · DDD C4).
import { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const scoreColor = (s: number) =>
  s >= 95 ? "text-green-500" : s >= 80 ? "text-amber-500" : "text-red-500";

export const fmtDateTime = (at: string) =>
  new Date(at).toLocaleString("es", { dateStyle: "short", timeStyle: "short" });

export const relativeAgo = (at: string) => {
  const m = Math.round((Date.now() - new Date(at).getTime()) / 60000);
  if (m < 1) return "recién";
  if (m < 60) return `hace ${m}m`;
  const h = Math.round(m / 60);
  return h < 24 ? `hace ${h}h` : `hace ${Math.round(h / 24)}d`;
};

// security_incidents.severity → color (critical/high/medium/low).
export const SEV_CLS: Record<string, string> = {
  critical: "bg-red-500/15 text-red-500 border-red-500/40",
  high: "bg-orange-500/15 text-orange-500 border-orange-500/40",
  medium: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  low: "bg-muted/40 text-muted-foreground border-border/40",
};

// ip_watchlist.list_type → color (block/watch/allow · esquema real 00022).
export const LIST_CLS: Record<string, string> = {
  block: "bg-red-500/15 text-red-500 border-red-500/40",
  watch: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  allow: "bg-green-500/15 text-green-500 border-green-500/40",
};

// Wrapper minimalista para volver un chip clickable SIN tocar el styling del Badge interno
// (cláusula de preservación visual · Sub-bloque B). Solo cursor + transición de opacidad.
export function IssueChip({ onClick, children }: { onClick: () => void; children: ReactNode }) {
  return (
    <button type="button" onClick={onClick} className="cursor-pointer transition-opacity hover:opacity-80">
      {children}
    </button>
  );
}

export function Section(props: { title: string; empty: boolean; emptyText: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">{props.title}</CardTitle></CardHeader>
      <CardContent className="space-y-1">
        {props.empty ? <p className="text-xs text-muted-foreground">{props.emptyText}</p> : props.children}
      </CardContent>
    </Card>
  );
}
