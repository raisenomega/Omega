import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { useMyClients } from "@/hooks/useMyClients";
import { useGenerateText } from "@/hooks/useGenerateText";
import { useGenerateImage } from "@/hooks/useGenerateImage";
import { VARIATIONS, type VariationLabel, type FormState } from "@/components/content/ContentLabFormV2";
import type { ResultV2, BlockState, ModalState } from "@/components/content/ResultCardV2";

const INITIAL_FORM: FormState = { platform: "instagram", type: "caption", tone: "casual", topic: "", braveQuery: "", clientId: "" };
const INITIAL_BLOCK: BlockState = { caption: null, image: null, hashtags: null };
const slotFor = (t: string): keyof BlockState => t === "image" ? "image" : t === "hashtags" ? "hashtags" : "caption";

export function useContentLabState() {
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
  const generateImage = useGenerateImage();

  const handleGenerate = async () => {
    const selected = VARIATIONS.filter(v => variations[v]);
    if (selected.length === 0) { toast({ title: "Seleccioná al menos una variación", variant: "destructive" }); return; }
    if (!form.topic.trim()) return;
    if (form.type === "video") { toast({ title: "Video próximamente · usá Caption/Hashtags/Image", variant: "destructive" }); return; }
    try {
      const mut = form.type === "image" ? generateImage : generateText;
      const newR = await mut.mutateAsync({ form, selectedLabels: selected });
      setResults(prev => [...prev, ...newR]);
      toast({ title: `${newR.length} resultado(s) generado(s) con ARIA` });
    } catch (e) {
      toast({ title: "Error generando", description: e instanceof Error ? e.message : "Unknown", variant: "destructive" });
    }
  };

  const handleAgendar = (r: ResultV2) => { setBlock(prev => ({ ...prev, [slotFor(r.content_type)]: r })); setModalState("open"); setExpandedResult(null); };
  const handleSave = (id: string) => { setResults(prev => prev.map(r => r.id === id ? { ...r, saved: true } : r)); toast({ title: "Guardado (mock V2)" }); };
  const handleDownload = (r: ResultV2) => toast({ title: `Descargar mock V2 · tipo: ${r.content_type}` });
  const handleConfirm = () => {
    const ids = [block.caption?.id, block.image?.id, block.hashtags?.id].filter(Boolean) as string[];
    setResults(prev => prev.filter(r => !ids.includes(r.id)));
    setBlock(INITIAL_BLOCK); setModalState("closed"); setScheduledAt("");
    toast({ title: `✅ Bloque programado para ${scheduledAt} (mock V2)` });
  };
  const handleResearch = () => toast({ title: "Brave Research en futuro Sprint" });

  return {
    form, setForm, variations, setVariations, results, setResults, clientList,
    block, modalState, setModalState, scheduledAt, setScheduledAt,
    expandedResult, setExpandedResult, slots: Math.max(4, results.length),
    handleGenerate, handleAgendar, handleSave, handleDownload, handleConfirm, handleResearch,
  };
}
