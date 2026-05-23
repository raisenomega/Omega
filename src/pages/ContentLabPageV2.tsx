import { Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { ContentLabFormV2 } from "@/components/content/ContentLabFormV2";
import { ContentLabFormBar } from "@/components/content/ContentLabFormBar";
import { ResultCardV2 } from "@/components/content/ResultCardV2";
import { ResultExpandedModal } from "@/components/content/ResultExpandedModal";
import { ScheduleModalV2 } from "@/components/content/ScheduleModalV2";
import { useContentLabState } from "@/hooks/useContentLabState";

export default function ContentLabPageV2() {
  const s = useContentLabState();
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-6 flex-wrap">
        <div className="shrink-0 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-amber-500" />
          <h1 className="text-2xl font-semibold">Content Lab</h1>
        </div>
        <div className="flex-1 min-w-[420px]">
          <ContentLabFormBar clientList={s.clientList ?? []} form={s.form} setForm={s.setForm}
            onResearch={s.handleResearch} />
        </div>
      </div>
      <div className="grid grid-cols-[280px_1fr_1fr] grid-rows-[220px_220px] items-stretch gap-3">
        <div className="row-span-full h-full">
          <ContentLabFormV2 form={s.form} setForm={s.setForm}
            variations={s.variations} setVariations={s.setVariations} onGenerate={s.handleGenerate} />
        </div>
        {Array.from({ length: s.slots }).map((_, i) => {
          const r = s.results[i];
          return r ? (
            <ResultCardV2 key={r.id} result={r} onExpand={s.setExpandedResult} onAgendar={s.handleAgendar}
              onSave={s.handleSave} onDownload={s.handleDownload} onRemove={(id) => s.setResults(p => p.filter(x => x.id !== id))} />
          ) : (
            <Card key={`empty-${i}`} className="h-full min-h-full border border-dashed border-muted-foreground/30 flex items-center justify-center bg-card/40">
              <p className="text-xs text-muted-foreground">próximo resultado</p>
            </Card>
          );
        })}
      </div>
      <ResultExpandedModal result={s.expandedResult} onClose={() => s.setExpandedResult(null)}
        onAgendar={s.handleAgendar} onSave={s.handleSave} onDownload={s.handleDownload} />
      <ScheduleModalV2 state={s.modalState} block={s.block} scheduledAt={s.scheduledAt} setScheduledAt={s.setScheduledAt}
        onMinimize={() => s.setModalState("minimized")} onRestore={() => s.setModalState("open")}
        onClose={() => s.setModalState("closed")} onConfirm={s.handleConfirm} />
    </div>
  );
}
