import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { useMyClients } from "@/hooks/useMyClients";
import { useGenerateText } from "@/hooks/useGenerateText";
import { useGenerateImage } from "@/hooks/useGenerateImage";
import { useVideoJobPolling } from "@/hooks/useVideoJobPolling";
import { useSaveContent } from "@/hooks/useContentActions";
import { downloadResult } from "@/lib/download-result";
import { useScheduleBlock } from "@/hooks/useScheduleBlock";
import { loadPersistedResults, persistResults } from "@/lib/content-lab-persistence";
import { VARIATIONS, type VariationLabel, type FormState } from "@/components/content/ContentLabFormV2";
import type { ResultV2, BlockState, ModalState } from "@/components/content/ResultCardV2";

const INITIAL_FORM: FormState = { platform: "instagram", type: "caption", tone: "casual", topic: "", braveQuery: "", clientId: "" };
const INITIAL_BLOCK: BlockState = { items: [] };

export function useContentLabState() {
  const { toast } = useToast();
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [variations, setVariations] = useState<Record<VariationLabel, boolean>>({ Conservadora: false, Balanceada: true, Atrevida: false });
  const [results, setResults] = useState<ResultV2[]>(loadPersistedResults);
  useEffect(() => { persistResults(results); }, [results]);
  const [block, setBlock] = useState<BlockState>(INITIAL_BLOCK);
  const [modalState, setModalState] = useState<ModalState>("closed");
  const [scheduledAt, setScheduledAt] = useState("");
  const [expandedResult, setExpandedResult] = useState<ResultV2 | null>(null);

  const { data: clientList } = useMyClients();
  const generateText = useGenerateText();
  const generateImage = useGenerateImage();
  const generateVideo = useVideoJobPolling();
  const saveContent = useSaveContent();
  const scheduleBlock = useScheduleBlock();

  const handleGenerate = async () => {
    const selected = VARIATIONS.filter(v => variations[v]);
    if (selected.length === 0) { toast({ title: "Seleccioná al menos una variación", variant: "destructive" }); return; }
    if (!form.topic.trim()) return;
    if (form.type === "video") {
      const tempId = `pending-${Date.now()}`;
      const placeholder: ResultV2 = { id: tempId, generated_text: "", content_type: "video", variation_label: selected[0], status: "pending" };
      setResults(prev => [...prev, placeholder]);
      try {
        const newR = await generateVideo.mutateAsync({ form, selectedLabels: selected });
        setResults(prev => prev.map(r => r.id === tempId ? newR[0] : r));
        toast({ title: "Video generado · listo para usar" });
      } catch (e) {
        setResults(prev => prev.filter(r => r.id !== tempId));
        toast({ title: "Error generando video", description: e instanceof Error ? e.message : "Unknown", variant: "destructive" });
      }
      return;
    }
    try {
      const mut = form.type === "image" ? generateImage : generateText;
      const newR = await mut.mutateAsync({ form, selectedLabels: selected });
      setResults(prev => [...prev, ...newR]);
      toast({ title: `${newR.length} resultado(s) generado(s) con ARIA` });
    } catch (e) {
      toast({ title: "Error generando", description: e instanceof Error ? e.message : "Unknown", variant: "destructive" });
    }
  };

  const handleAgendar = (r: ResultV2) => { setBlock(prev => ({ items: [...prev.items, r] })); setModalState("open"); setExpandedResult(null); };
  const handleRemoveItem = (i: number) => setBlock(prev => ({ items: prev.items.filter((_, j) => j !== i) }));
  const handleSave = (id: string) => {
    saveContent.mutate({ id, is_saved: true }, {
      onSuccess: () => setResults(prev => prev.map(r => r.id === id ? { ...r, saved: true } : r)),
    });
  };
  const handleDownload = async (r: ResultV2) => {
    try { await downloadResult(r); toast({ title: "Descarga iniciada" }); }
    catch (e) { toast({ title: "Error al descargar", description: e instanceof Error ? e.message : "", variant: "destructive" }); }
  };
  const handleConfirm = async () => {
    if (!form.clientId) { toast({ title: "Falta seleccionar cliente", variant: "destructive" }); return; }
    try {
      await scheduleBlock.mutateAsync({ block, clientId: form.clientId, platform: form.platform, scheduledAt });
      const ids = block.items.map(i => i.id);
      setResults(prev => prev.filter(r => !ids.includes(r.id)));
      setBlock(INITIAL_BLOCK); setModalState("closed"); setScheduledAt("");
      toast({ title: `✅ Bloque programado para ${scheduledAt}` });
    } catch (e) {
      toast({ title: "Error al agendar", description: e instanceof Error ? e.message : "", variant: "destructive" });
    }
  };
  const handleResearch = () => toast({ title: "Brave Research en futuro Sprint" });

  const isPending = generateText.isPending || generateImage.isPending || generateVideo.isPending;
  return {
    form, setForm, variations, setVariations, results, setResults, clientList,
    block, modalState, setModalState, scheduledAt, setScheduledAt,
    expandedResult, setExpandedResult, slots: Math.max(4, results.length), isPending,
    handleGenerate, handleAgendar, handleRemoveItem, handleSave, handleDownload, handleConfirm, handleResearch,
  };
}
