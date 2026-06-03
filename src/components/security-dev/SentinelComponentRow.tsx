import { useState, type ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { ChevronDown } from "lucide-react";
import { relativeAgo, scoreColor } from "./parts";
import type { ComponentSummary } from "@/lib/sentinel_component_summary";

const TONE_CLS: Record<ComponentSummary["tone"], string> = {
  ok: "bg-green-500/15 text-green-500 border-green-500/40",
  warn: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  bad: "bg-red-500/15 text-red-500 border-red-500/40",
  none: "bg-muted/40 text-muted-foreground border-border/40",
};

// Fila colapsable de "Estado por componente": header resumen + cuerpo (card de detalle existente).
export function SentinelComponentRow({ name, summary, children }: { name: string; summary: ComponentSummary; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-border/40">
      <button onClick={() => setOpen((v) => !v)} className="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm">
        <span className="font-medium">{name}</span>
        <span className="flex items-center gap-2">
          {summary.score != null && <span className={`text-sm font-semibold ${scoreColor(summary.score)}`}>{summary.score}</span>}
          <Badge variant="outline" className={TONE_CLS[summary.tone]}>{summary.label}</Badge>
          <span className="hidden text-[10px] text-muted-foreground sm:inline">
            {summary.lastRun ? relativeAgo(summary.lastRun) : "sin corridas"}
          </span>
          <ChevronDown className={`h-4 w-4 transition-transform ${open ? "" : "-rotate-90"}`} />
        </span>
      </button>
      {open && <div className="p-3 pt-0">{children}</div>}
    </div>
  );
}
