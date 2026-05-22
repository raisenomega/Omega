import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Loader2, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { PillGroup } from "@/components/onboarding/PillGroup";
import { PLATFORMS, PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { useSaveContent } from "@/hooks/useContentActions";
import { ResultCard, Result } from "@/components/content/ResultCard";
import { useVideoJobPolling } from "@/hooks/useVideoJobPolling";
import { generateText, generateImage, generateVideo } from "@/lib/content-lab-api";
import {
  TYPES, TONES, STYLES, RATIOS,
  TYPE_LABELS, TONE_LABELS, STYLE_LABELS, RATIO_LABELS,
} from "@/lib/content-lab-constants";

export default function ContentLabPage() {
  const { toast } = useToast();
  useTrackOnMount("feature_open", { feature: "content_lab" });
  const [platform, setPlatform] = useState<string>("instagram"), [type, setType] = useState<string>("caption");
  const [topic, setTopic] = useState(""), [tone, setTone] = useState<string>("casual");
  const [style, setStyle] = useState<string>("realistic"), [ratio, setRatio] = useState<string>("1280:768");
  const [variationsOn, setVariationsOn] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const save = useSaveContent();
  const isImage = type === "image", isVideo = type === "video";

  useVideoJobPolling(
    jobId,
    (url, id) => { setResult({ id, generated_text: url, content_type: "video" }); setJobId(null); toast({ title: "Video listo" }); },
    (err) => { setJobId(null); toast({ title: "Video falló", description: err, variant: "destructive" }); },
  );

  const m = useMutation({
    mutationFn: async () => {
      setResult(null); setJobId(null);
      if (isVideo) return generateVideo({ prompt: topic, ratio });
      if (isImage) return generateImage({ prompt: topic, style });
      return generateText({ platform, content_type: type, topic, tone, variations: variationsOn ? 3 : 1 });
    },
    onSuccess: (r) => {
      if ("job_id" in r) { setJobId(r.job_id); toast({ title: "Video en cola · 30-90s" }); }
      else { setResult(r as Result); toast({ title: isImage ? "Imagen generada" : (variationsOn ? "3 variaciones generadas" : "Contenido generado") }); }
    },
    onError: (e: Error) => {
      const isProGate = e.message.includes("variations_require_pro");
      toast({ title: isProGate ? "Plan PRO requerido" : "No se pudo generar", description: isProGate ? "Las 3 variaciones requieren plan PRO. Actualizá en Configuración." : e.message, variant: "destructive" });
    },
  });
  const isPolling = !!jobId, isPending = m.isPending || isPolling;

  return (
    <div className="container mx-auto max-w-3xl px-4 py-6 space-y-4">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold flex items-center gap-2"><Sparkles className="h-5 w-5 text-amber-500" />Content Lab</h1>
        <p className="text-sm text-muted-foreground">Genera contenido con ARIA.</p>
      </header>
      <Card><CardContent className="space-y-3 p-4">
        <div className="space-y-1"><Label className="text-xs">Plataforma</Label>
          <PillGroup options={PLATFORMS} labels={PLATFORM_LABELS} value={platform} onChange={(x) => setPlatform(x as string)} cols={3} /></div>
        <div className="space-y-1"><Label className="text-xs">Tipo</Label>
          <PillGroup options={TYPES} labels={TYPE_LABELS} value={type} onChange={(x) => setType(x as string)} cols={5} /></div>
        <div className="space-y-1"><Label className="text-xs">{isImage || isVideo ? "Prompt visual" : "Tema"}</Label>
          <Textarea value={topic} onChange={(e) => setTopic(e.target.value)} rows={3} placeholder={isVideo ? "Describe el video (Veo 3.1 · 8s)" : isImage ? "Describe la imagen que quieres generar" : "¿De qué trata este post?"} className="resize-none" /></div>
        {isImage && (<div className="space-y-1"><Label className="text-xs">Estilo</Label>
          <PillGroup options={STYLES} labels={STYLE_LABELS} value={style} onChange={(x) => setStyle(x as string)} cols={3} /></div>)}
        {isVideo && (<div className="space-y-1"><Label className="text-xs">Formato</Label>
          <PillGroup options={RATIOS} labels={RATIO_LABELS} value={ratio} onChange={(x) => setRatio(x as string)} cols={2} /></div>)}
        {!isImage && !isVideo && (<>
          <div className="space-y-1"><Label className="text-xs">Tono</Label>
            <PillGroup options={TONES} labels={TONE_LABELS} value={tone} onChange={(x) => setTone(x as string)} cols={3} /></div>
          <div className="flex items-center gap-2 pt-1">
            <Switch checked={variationsOn} onCheckedChange={setVariationsOn} id="variations-switch" />
            <Label htmlFor="variations-switch" className="text-xs cursor-pointer">Generar 3 variaciones A/B/C <Badge variant="outline" className="ml-1 h-4 text-[9px]">PRO</Badge></Label>
          </div>
        </>)}
        <Button onClick={() => m.mutate()} disabled={isPending || !topic.trim()} className="w-full gap-1 bg-amber-500 hover:bg-amber-600 text-white">
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {isPolling ? "Generando video… (30-90s)" : m.isPending ? "Iniciando…" : "Generar con ARIA"}
        </Button>
      </CardContent></Card>
      {result && <ResultCard result={result} onSave={(id) => save.mutate({ id, is_saved: true })} onRegenerate={() => m.mutate()} isSaving={save.isPending} isPending={isPending} />}
    </div>
  );
}
