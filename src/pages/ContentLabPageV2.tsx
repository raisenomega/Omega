import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { ContentLabFormV2, VARIATIONS, type VariationLabel, type FormState } from "@/components/content/ContentLabFormV2";
import { ResultGridV2 } from "@/components/content/ResultGridV2";
import { ScheduleModalV2 } from "@/components/content/ScheduleModalV2";
import type { ResultV2, BlockState, ModalState } from "@/components/content/ResultCardV2";

const MOCK_TEXTS = [
  "Cada plato es una historia familiar. Nuestro mofongo · tradición de generaciones. Probá lo auténtico hoy. 🍌👨‍🍳 ¿Cuál es tu favorito?",
  "El sabor de la abuela, en cada bocado. 3 generaciones cocinando con amor. Reservá tu mesa para esta semana. #ComidaCriolla #PR",
  "🔥 LO QUE NADIE TE DICE del mofongo: el secreto está en el ajo MAJADO a mano. Ven y descubrí la diferencia. Solo este sábado.",
];

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

  const { data: clientList } = useQuery({
    queryKey: ["lab_clients_v2"],
    queryFn: async () => (await supabase.from("clients").select("id, name").order("name").limit(20)).data ?? [],
  });

  const handleGenerate = () => {
    const selected = VARIATIONS.filter(v => variations[v]);
    if (selected.length === 0) { toast({ title: "Seleccioná al menos una variación", variant: "destructive" }); return; }
    if (!form.topic.trim()) return;
    const newR: ResultV2[] = selected.map((label, i) => ({
      id: `mock-${Date.now()}-${i}`, generated_text: MOCK_TEXTS[VARIATIONS.indexOf(label) % 3],
      content_type: form.type, variation_label: label,
      virality_score: 70 + Math.floor(Math.random() * 25), virality_estimated: true,
    }));
    setResults(prev => [...prev, ...newR]);
    toast({ title: `${selected.length} resultado(s) agregados al grid` });
  };

  const slotFor = (t: string): keyof BlockState => t === "image" ? "image" : t === "hashtags" ? "hashtags" : "caption";
  const handleAgendar = (r: ResultV2) => { setBlock(prev => ({ ...prev, [slotFor(r.content_type)]: r })); setModalState("open"); };
  const handleSave = (id: string) => { setResults(prev => prev.map(r => r.id === id ? { ...r, saved: true } : r)); toast({ title: "Guardado (mock V2)" }); };
  const handleDownload = (r: ResultV2) => toast({ title: `Descargar mock V2 · tipo: ${r.content_type}` });
  const handleConfirm = () => {
    const ids = [block.caption?.id, block.image?.id, block.hashtags?.id].filter(Boolean) as string[];
    setResults(prev => prev.filter(r => !ids.includes(r.id)));
    setBlock(INITIAL_BLOCK); setModalState("closed"); setScheduledAt("");
    toast({ title: `✅ Bloque programado para ${scheduledAt} (mock V2)` });
  };

  return (
    <div className="container mx-auto max-w-4xl px-4 py-6 space-y-4">
      <header className="flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-amber-500" />
        <h1 className="text-2xl font-semibold">Content Lab V2</h1>
        <span className="text-xs text-muted-foreground">(mock · iteración visual)</span>
      </header>
      <ContentLabFormV2
        clientList={clientList ?? []}
        form={form} setForm={setForm}
        variations={variations} setVariations={setVariations}
        onGenerate={handleGenerate}
        onResearch={() => toast({ title: "Brave Research en futuro Sprint" })}
      />
      <ResultGridV2 results={results} onAgendar={handleAgendar} onSave={handleSave} onDownload={handleDownload} />
      <ScheduleModalV2
        state={modalState} block={block} scheduledAt={scheduledAt} setScheduledAt={setScheduledAt}
        onMinimize={() => setModalState("minimized")} onRestore={() => setModalState("open")}
        onClose={() => setModalState("closed")} onConfirm={handleConfirm}
      />
    </div>
  );
}
