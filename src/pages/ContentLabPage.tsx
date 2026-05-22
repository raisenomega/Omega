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
import { supabase } from "@/integrations/supabase/client";
import { PillGroup } from "@/components/onboarding/PillGroup";
import { PLATFORMS, PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { useSaveContent } from "@/hooks/useContentActions";
import { ResultCard, Result } from "@/components/content/ResultCard";

const TYPES = ["caption", "hashtags", "video_script", "image"] as const;
const TONES = ["profesional", "casual", "inspirador", "educativo", "divertido"] as const;
const STYLES = ["realistic", "cartoon", "minimal"] as const;
const TYPE_LABELS = { caption: "Caption", hashtags: "Hashtags", video_script: "Video Script", image: "Imagen" } as const;
const TONE_LABELS = { profesional: "Profesional", casual: "Casual", inspirador: "Inspirador", educativo: "Educativo", divertido: "Divertido" } as const;
const STYLE_LABELS = { realistic: "Realista", cartoon: "Cartoon", minimal: "Minimal" } as const;

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession();
  const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  const r = await fetch(`${base}${path}`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` }, body: JSON.stringify(body) });
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${r.status}`); }
  return r.json();
}

const generateText = (b: { platform: string; content_type: string; topic: string; tone: string; variations: number }) => apiPost<Result>("/content-lab/generate", b);
const generateImage = (b: { prompt: string; style: string }) => apiPost<Result>("/content-lab/generate-image", b);

export default function ContentLabPage() {
  const { toast } = useToast();
  useTrackOnMount("feature_open", { feature: "content_lab" });
  const [platform, setPlatform] = useState<string>("instagram"), [type, setType] = useState<string>("caption");
  const [topic, setTopic] = useState(""), [tone, setTone] = useState<string>("casual"), [style, setStyle] = useState<string>("realistic");
  const [variationsOn, setVariationsOn] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const save = useSaveContent();
  const isImage = type === "image";
  const m = useMutation({
    mutationFn: () => isImage ? generateImage({ prompt: topic, style }) : generateText({ platform, content_type: type, topic, tone, variations: variationsOn ? 3 : 1 }),
    onSuccess: (r) => { setResult(r); toast({ title: isImage ? "Imagen generada" : (variationsOn ? "3 variaciones generadas" : "Contenido generado") }); },
    onError: (e: Error) => {
      const isProGate = e.message.includes("variations_require_pro");
      toast({ title: isProGate ? "Plan PRO requerido" : "No se pudo generar", description: isProGate ? "Las 3 variaciones requieren plan PRO. Actualizá en Configuración." : e.message, variant: "destructive" });
    },
  });

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
          <PillGroup options={TYPES} labels={TYPE_LABELS} value={type} onChange={(x) => setType(x as string)} cols={4} />
          <p className="text-[10px] text-muted-foreground mt-1 flex items-center gap-1">Video <Badge variant="outline" className="h-4 text-[9px]">Próximamente</Badge></p></div>
        <div className="space-y-1"><Label className="text-xs">{isImage ? "Prompt visual" : "Tema"}</Label>
          <Textarea value={topic} onChange={(e) => setTopic(e.target.value)} rows={3} placeholder={isImage ? "Describe la imagen que quieres generar" : "¿De qué trata este post?"} className="resize-none" /></div>
        {isImage ? (
          <div className="space-y-1"><Label className="text-xs">Estilo</Label>
            <PillGroup options={STYLES} labels={STYLE_LABELS} value={style} onChange={(x) => setStyle(x as string)} cols={3} /></div>
        ) : (
          <>
            <div className="space-y-1"><Label className="text-xs">Tono</Label>
              <PillGroup options={TONES} labels={TONE_LABELS} value={tone} onChange={(x) => setTone(x as string)} cols={3} /></div>
            <div className="flex items-center gap-2 pt-1">
              <Switch checked={variationsOn} onCheckedChange={setVariationsOn} id="variations-switch" />
              <Label htmlFor="variations-switch" className="text-xs cursor-pointer">Generar 3 variaciones A/B/C <Badge variant="outline" className="ml-1 h-4 text-[9px]">PRO</Badge></Label>
            </div>
          </>
        )}
        <Button onClick={() => m.mutate()} disabled={m.isPending || !topic.trim()} className="w-full gap-1 bg-amber-500 hover:bg-amber-600 text-white">
          {m.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}{m.isPending ? "Generando…" : "Generar con ARIA"}
        </Button>
      </CardContent></Card>
      {result && <ResultCard result={result} onSave={(id) => save.mutate({ id, is_saved: true })} onRegenerate={() => m.mutate()} isSaving={save.isPending} isPending={m.isPending} />}
    </div>
  );
}
