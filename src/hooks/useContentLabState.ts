import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useGenerateText } from "@/hooks/useGenerateText";
import { useGenerateImage } from "@/hooks/useGenerateImage";
import { useVideoJobPolling } from "@/hooks/useVideoJobPolling";
import { useSaveContent } from "@/hooks/useContentActions";
import { downloadResult } from "@/lib/download-result";
import { useScheduleBlock } from "@/hooks/useScheduleBlock";
import { useResearch } from "@/hooks/useResearch";
import { loadPersistedResults, persistResults } from "@/lib/content-lab-persistence";
import { VARIATIONS, type VariationLabel, type FormState } from "@/components/content/ContentLabFormV2";
import type { ResultV2, BlockState, ModalState } from "@/components/content/ResultCardV2";

const INITIAL_FORM: FormState = { platform: "instagram", type: "caption", tone: "casual", topic: "", braveQuery: "", clientId: "", aspect: "1:1", accountId: "", applyLogo: false };
const INITIAL_BLOCK: BlockState = { items: [] };

export function useContentLabState(activeBusinessId: string | null) {
  const { toast } = useToast();
  // Brief CTA (Centro de Inteligencia): si llegamos con location.state.brief, lo pre-cargamos en el topic.
  // Defensivo: si no hay brief válido → INITIAL_FORM intacto.
  const location = useLocation();
  const navState = location.state as { brief?: unknown; referenceImageUrl?: unknown } | null;
  const refImageUrl = typeof navState?.referenceImageUrl === "string" && navState.referenceImageUrl.trim()
    ? navState.referenceImageUrl : undefined;
  const [form, setForm] = useState<FormState>(() => {
    const brief = navState?.brief;
    const base = typeof brief === "string" && brief.trim() ? { ...INITIAL_FORM, topic: brief } : INITIAL_FORM;
    // TAREA 2 · si llegamos con referenceImageUrl, arrancamos en type=image desde el 1er render.
    // Así el reset por cambio de type (DEBT-CL-020) NO se dispara al setear la imagen async (evita wipe).
    return refImageUrl ? { ...base, type: "image" } : base;
  });
  // TAREA 2 · "Usar en Content Lab" desde Media: fetch de referenceImageUrl → base64 raw
  // (sin prefijo data: · igual que PromptAttachmentControls) → reference_image_b64.
  // Best-effort: si el fetch falla, toast suave y form intacto. Sin referenceImageUrl → comportamiento intacto.
  useEffect(() => {
    if (!refImageUrl) return;
    let cancelled = false;
    fetch(refImageUrl)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.blob(); })
      .then(blob => new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve((reader.result as string).split(",")[1] ?? "");
        reader.onerror = () => reject(reader.error ?? new Error("read failed"));
        reader.readAsDataURL(blob);
      }))
      .then(b64 => { if (!cancelled && b64) setForm(prev => ({ ...prev, reference_image_b64: b64 })); })
      .catch(() => { if (!cancelled) toast({ title: "No se pudo cargar la imagen de referencia" }); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  // DEBT-CL-015: reset accountId cuando cambia clientId o platform (evita huérfanos)
  useEffect(() => { setForm(prev => ({ ...prev, accountId: "" })); }, [form.clientId, form.platform]);
  // DEBT-CL-020: reset attachments cuando cambia type (un caption no necesita imagen ref · evita confusión)
  useEffect(() => { setForm(prev => ({ ...prev, reference_image_b64: undefined, reference_attachment_b64: undefined, reference_mime_type: undefined })); }, [form.type]);
  const [variations, setVariations] = useState<Record<VariationLabel, boolean>>({ Conservadora: false, Balanceada: true, Atrevida: false });
  const [results, setResults] = useState<ResultV2[]>(() => loadPersistedResults(activeBusinessId));
  // Al cambiar de negocio, recargá SUS results (cada negocio su cache · aísla la grilla).
  useEffect(() => { setResults(loadPersistedResults(activeBusinessId)); }, [activeBusinessId]);
  // Persistí SOLO cuando cambian los results (dep [results], NO activeBusinessId · intencional): en el render
  // del switch los results viejos NO se re-escriben al key nuevo; tras la recarga el persist corre con el
  // negocio nuevo. Por eso el dep array es más angosto que el closure read.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { persistResults(activeBusinessId, results); }, [results]);
  const [block, setBlock] = useState<BlockState>(INITIAL_BLOCK);
  const [modalState, setModalState] = useState<ModalState>("closed");
  const [scheduledAt, setScheduledAt] = useState("");
  const [expandedResult, setExpandedResult] = useState<ResultV2 | null>(null);

  const generateText = useGenerateText();
  const generateImage = useGenerateImage();
  const generateVideo = useVideoJobPolling();
  const saveContent = useSaveContent();
  const scheduleBlock = useScheduleBlock();

  // DEBT-CL-010: cleanup auto-cancela video pending al unmount (zombie polling fix)
  useEffect(() => () => { generateVideo.cancel(); }, [generateVideo]);

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
    // clientId siempre = activeBusinessId (Switcher V1 · sync en ContentLabPageV2) · guard defensivo
    if (!form.clientId) { toast({ title: "Falta seleccionar cliente", variant: "destructive" }); return; }
    try {
      await scheduleBlock.mutateAsync({ block, clientId: form.clientId, platform: form.platform, scheduledAt, accountId: form.accountId });
      const ids = block.items.map(i => i.id);
      setResults(prev => prev.filter(r => !ids.includes(r.id)));
      setBlock(INITIAL_BLOCK); setModalState("closed"); setScheduledAt("");
      toast({ title: `✅ Bloque programado para ${scheduledAt}` });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "";
      if (msg.startsWith("content_not_found:")) {  // backend 409 · ids stale del localStorage
        const stale = new Set(msg.slice("content_not_found:".length).split(",").filter(Boolean));
        setBlock(prev => ({ items: prev.items.filter(i => !stale.has(i.id)) }));
        setResults(prev => prev.filter(r => !stale.has(r.id)));  // persistResults() limpia localStorage
        toast({ title: "Estos contenidos ya no existen, regeneralos", variant: "destructive" });
        return;
      }
      toast({ title: "Error al agendar", description: msg, variant: "destructive" });
    }
  };
  // Brave Search · resultados aparecen como cards en el grid (mismo UX que outputs generados)
  // Spec owner: "resultado pop-up como resultado de generar cualquier type de orquestador"
  const research = useResearch();
  const handleResearch = () => {
    const q = form.braveQuery.trim();
    if (q.length < 3) { toast({ title: "Query muy corta", description: "Mínimo 3 caracteres", variant: "destructive" }); return; }
    research.mutate({ query: q, max_results: 5 }, {
      onSuccess: (r) => {
        const mapped: ResultV2[] = r.results.map((res, i) => ({
          id: `research-${Date.now()}-${i}`,
          generated_text: res.snippet,
          content_type: "research",
          title: res.title,
          url: res.url,
          snippet: res.snippet,
        }));
        setResults(prev => [...prev, ...mapped]);
        toast({ title: `${r.results.length} resultado(s) web · ${r.duration_ms}ms` });
      },
      onError: (e) => toast({ title: "Brave Search falló", description: e.message, variant: "destructive" }),
    });
  };
  const appendSnippetToTopic = (snippet: string) => {
    setForm(prev => ({ ...prev, topic: prev.topic ? `${prev.topic}\n\nContexto web: ${snippet}` : `Contexto web: ${snippet}` }));
  };
  // DEBT-CL-010: user clica X en placeholder pending video · cancel + clean
  const handleCancelVideo = (tempId: string) => {
    generateVideo.cancel();
    setResults(prev => prev.filter(r => r.id !== tempId));
    toast({ title: "Video cancelado" });
  };

  const isPending = generateText.isPending || generateImage.isPending || generateVideo.isPending;
  return {
    form, setForm, variations, setVariations, results, setResults,
    block, modalState, setModalState, scheduledAt, setScheduledAt,
    expandedResult, setExpandedResult, slots: Math.max(4, results.length), isPending,
    handleGenerate, handleAgendar, handleRemoveItem, handleSave, handleDownload, handleConfirm, handleResearch, handleCancelVideo,
    isResearching: research.isPending, appendSnippetToTopic,
  };
}
