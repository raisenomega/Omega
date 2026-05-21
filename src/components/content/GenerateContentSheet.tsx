import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, Sparkles } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";
import { PillGroup } from "@/components/onboarding/PillGroup";
import { PLATFORMS, PLATFORM_LABELS } from "@/lib/onboarding-constants";

const TYPES = ["caption", "hashtags", "video_script"] as const;
const TYPE_LABELS = { caption: "Caption", hashtags: "Hashtags", video_script: "Video Script" } as const;
const TONES = ["profesional", "casual", "inspirador", "educativo", "divertido"] as const;
const TONE_LABELS = { profesional: "Profesional", casual: "Casual", inspirador: "Inspirador", educativo: "Educativo", divertido: "Divertido" } as const;

async function generateContent(body: { platform: string; content_type: string; topic: string; tone: string }) {
  const { data: { session } } = await supabase.auth.getSession();
  const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  const r = await fetch(`${base}/content-lab/generate`, {
    method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` },
    body: JSON.stringify(body),
  });
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${r.status}`); }
  return r.json();
}

interface GenerateContentSheetProps { open: boolean; onOpenChange: (o: boolean) => void }

export function GenerateContentSheet({ open, onOpenChange }: GenerateContentSheetProps) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [platform, setPlatform] = useState<string>("instagram");
  const [type, setType] = useState<string>("caption");
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState<string>("casual");

  const m = useMutation({
    mutationFn: () => generateContent({ platform, content_type: type, topic, tone }),
    onSuccess: () => { toast({ title: "Contenido generado", description: "Revísalo en Pendientes" }); qc.invalidateQueries({ queryKey: ["content_list"] }); setTopic(""); onOpenChange(false); },
    onError: (e: Error) => toast({ title: "No se pudo generar", description: e.message, variant: "destructive" }),
  });

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md flex flex-col gap-3">
        <SheetHeader><SheetTitle className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-primary" />Generar contenido</SheetTitle></SheetHeader>
        <div className="space-y-3 flex-1 overflow-y-auto">
          <div className="space-y-1"><Label className="text-xs">Plataforma</Label>
            <PillGroup options={PLATFORMS} labels={PLATFORM_LABELS} value={platform} onChange={(x) => setPlatform(x as string)} cols={3} />
          </div>
          <div className="space-y-1"><Label className="text-xs">Tipo</Label>
            <PillGroup options={TYPES} labels={TYPE_LABELS} value={type} onChange={(x) => setType(x as string)} cols={3} />
          </div>
          <div className="space-y-1"><Label className="text-xs">Tema</Label>
            <Textarea value={topic} onChange={(e) => setTopic(e.target.value)} rows={3} placeholder="¿De qué trata este post?" className="resize-none" />
          </div>
          <div className="space-y-1"><Label className="text-xs">Tono</Label>
            <PillGroup options={TONES} labels={TONE_LABELS} value={tone} onChange={(x) => setTone(x as string)} cols={3} />
          </div>
        </div>
        <div className="flex gap-2 pt-2 border-t border-border">
          <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">Cancelar</Button>
          <Button onClick={() => m.mutate()} disabled={m.isPending || !topic.trim()} className="flex-1 gap-1 bg-amber-500 hover:bg-amber-600 text-white">
            {m.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            {m.isPending ? "Generando…" : "Generar con ARIA"}
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
