import { useState } from "react";
import { Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useMyClients } from "@/hooks/useMyClients";
import { useGenerateText } from "@/hooks/useGenerateText";
import { Card } from "@/components/ui/card";
import { ContentLabFormV2, VARIATIONS, type VariationLabel, type FormState } from "@/components/content/ContentLabFormV2";
import { ContentLabFormBar } from "@/components/content/ContentLabFormBar";
import { ResultCardV2 } from "@/components/content/ResultCardV2";
import { ResultExpandedModal } from "@/components/content/ResultExpandedModal";
import { ScheduleModalV2 } from "@/components/content/ScheduleModalV2";
import type { ResultV2, BlockState, ModalState } from "@/components/content/ResultCardV2";

const INITIAL_FORM: FormState = { platform: "instagram", type: "caption", tone: "casual", topic: "", braveQuery: "", clientId: "" };
const INITIAL_BLOCK: BlockState = { caption: null, image: null, hashtags: null };

export default function ContentLabPageV2() {
  const { toast } = useToast();
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [variations, setVariations] = useState<Record<VariationLabel, boolean>>({ Conservadora: false, Balanceada: true, Atrevida: false });
  const [results, setResults] = useState<ResultV2[]>([]);
  const [block, setBlock] = useState<BlockState>(INITIAL_BLOCK);
  const [modalState, setModalState] = useState<ModalState>("closed");
  const [scheduledAt, setScheduledAt] = useState("");
  const [expandedResult, setExpandedResult] = useState<ResultV2 | null>(null);

  const { data: clientList } = useMyClients();
  const generateText = useGenerateText();

  const handleGenerate = async () => {
    const selected = VARIATIONS.filter(v => variations[v]);
    if (selected.length === 0) { toast({ title: "Seleccioná al menos una variación", variant: "destructive" }); return; }
    if (!form.topic.trim()) return;
    if (form.type === "image" || form.type === "video") {
      toast({ title: `Tipo "${form.type}" próximamente · usá Caption/Hashtags por ahora`, variant: "destructive" });
      return;
    }
    try {
      const newR = await generateText.mutateAsync({ form, selectedLabels: selected });
      setResults(prev => [...prev, ...newR]);
      toast({ title: `${newR.length} resultado(s) generado(s) con ARIA` });
    } catch (e) {
      toast({ title: "Error generando", description: e instanceof Error ? e.message : "Unknown", variant: "destructive" });
    }
  };

  const slotFor = (t: string): keyof BlockState => t === "image" ? "image" : t === "hashtags" ? "hashtags" : "caption";
  const handleAgendar = (r: ResultV2) => { setBlock(prev => ({ ...prev, [slotFor(r.content_type)]: r })); setModalState("open"); setExpandedResult(null); };
  const handleSave = (id: string) => { setResults(prev => prev.map(r => r.id === id ? { ...r, saved: true } : r)); toast({ title: "Guardado (mock V2)" }); };
  const handleDownload = (r: ResultV2) => toast({ title: `Descargar mock V2 · tipo: ${r.content_type}` });
  const handleConfirm = () => {
    const ids = [block.caption?.id, block.image?.id, block.hashtags?.id].filter(Boolean) as string[];
    setResults(prev => prev.filter(r => !ids.includes(r.id)));
    setBlock(INITIAL_BLOCK); setModalState("closed"); setScheduledAt("");
    toast({ title: `✅ Bloque programado para ${scheduledAt} (mock V2)` });
  };

  const slots = Math.max(4, results.length);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-6 flex-wrap">
        <div className="shrink-0 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-amber-500" />
          <h1 className="text-2xl font-semibold">Content Lab</h1>
        </div>
        <div className="flex-1 min-w-[420px]">
          <ContentLabFormBar clientList={clientList ?? []} form={form} setForm={setForm}
            onResearch={() => toast({ title: "Brave Research en futuro Sprint" })} />
        </div>
      </div>
      <div className="grid grid-cols-[280px_1fr_1fr] grid-rows-[220px_220px] items-stretch gap-3">
        <div className="row-span-full h-full">
          <ContentLabFormV2 form={form} setForm={setForm}
            variations={variations} setVariations={setVariations} onGenerate={handleGenerate} />
        </div>
        {Array.from({ length: slots }).map((_, i) => {
          const r = results[i];
          return r ? (
            <ResultCardV2 key={r.id} result={r} onExpand={setExpandedResult} onAgendar={handleAgendar}
              onSave={handleSave} onDownload={handleDownload} onRemove={(id) => setResults(p => p.filter(x => x.id !== id))} />
          ) : (
            <Card key={`empty-${i}`} className="h-full min-h-full border border-dashed border-muted-foreground/30 flex items-center justify-center bg-card/40">
              <p className="text-xs text-muted-foreground">próximo resultado</p>
            </Card>
          );
        })}
      </div>
      <ResultExpandedModal result={expandedResult} onClose={() => setExpandedResult(null)}
        onAgendar={handleAgendar} onSave={handleSave} onDownload={handleDownload} />
      <ScheduleModalV2 state={modalState} block={block} scheduledAt={scheduledAt} setScheduledAt={setScheduledAt}
        onMinimize={() => setModalState("minimized")} onRestore={() => setModalState("open")}
        onClose={() => setModalState("closed")} onConfirm={handleConfirm} />
    </div>
  );
}
