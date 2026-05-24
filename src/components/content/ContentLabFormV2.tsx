import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useImprovePrompt } from "@/hooks/useImprovePrompt";
import { ImprovePromptPanel } from "./ImprovePromptPanel";

export const VARIATIONS = ["Conservadora", "Balanceada", "Atrevida"] as const;
export type VariationLabel = typeof VARIATIONS[number];

export const ASPECTS = ["1:1", "9:16", "16:9"] as const;
export type Aspect = typeof ASPECTS[number];
const ASPECT_LABELS: Record<Aspect, string> = { "1:1": "Cuadrado", "9:16": "Story", "16:9": "Landscape" };

export interface FormState {
  platform: string; type: string; tone: string; topic: string; braveQuery: string; clientId: string;
  aspect: Aspect;
  reference_image_b64?: string;  // UX-6 · imagen de referencia opcional para edición
}

const MAX_REF_IMAGE_BYTES = 5 * 1024 * 1024;  // 5MB cap base64-encoded

interface Props {
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  variations: Record<VariationLabel, boolean>;
  setVariations: React.Dispatch<React.SetStateAction<Record<VariationLabel, boolean>>>;
  onGenerate: () => void;
  isPending?: boolean;
}

export function ContentLabFormV2({ form, setForm, variations, setVariations, onGenerate, isPending }: Props) {
  const update = <K extends keyof FormState>(k: K, v: FormState[K]) => setForm(prev => ({ ...prev, [k]: v }));
  const hasVar = Object.values(variations).some(Boolean);
  const [improvedText, setImprovedText] = useState<string | null>(null);
  const improve = useImprovePrompt();
  const handleImprove = () => improve.mutate(
    { original_prompt: form.topic, platform: form.platform, content_type: form.type },
    { onSuccess: (d) => setImprovedText(d.improved_prompt) }
  );

  const handleRefImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_REF_IMAGE_BYTES) { alert("Imagen >5MB · usá una más pequeña"); return; }
    const reader = new FileReader();
    reader.onload = () => update("reference_image_b64", (reader.result as string).split(",")[1] ?? "");
    reader.readAsDataURL(file);
  };

  return (
    <div className="space-y-3 h-full flex flex-col">
      {improvedText && (
        <ImprovePromptPanel improvedText={improvedText}
          onAccept={() => { update("topic", improvedText); setImprovedText(null); }}
          onReject={() => setImprovedText(null)} />
      )}
      {/* CAJÓN AMARILLO · Prompt principal (flex-1 ocupa altura disponible) */}
      <div className="bg-background border-2 border-amber-500 rounded-lg p-3 flex-1 flex flex-col relative">
        <Textarea value={form.topic} onChange={(e) => update("topic", e.target.value)}
          className="bg-transparent border-none outline-none resize-none w-full h-full focus:ring-0 focus-visible:ring-0 flex-1 min-h-[120px]" />
        <Button size="sm" variant="ghost" onClick={handleImprove}
          disabled={!form.topic.trim() || improve.isPending}
          className="absolute bottom-2 right-2 h-7 text-[11px] gap-1 text-amber-700 hover:bg-amber-100 dark:hover:bg-amber-950/30">
          {improve.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
          Mejorar
        </Button>
      </div>
      {/* CHECKBOXES VARIACIONES + ASPECT (UX-4 + UX-3) · 1 línea compacta */}
      <div className="flex flex-nowrap gap-2 items-center justify-center py-1">
        {VARIATIONS.map(v => (
          <div key={v} className="flex items-center gap-1">
            <Checkbox id={`var-${v}`} checked={variations[v]} onCheckedChange={(c) => setVariations(prev => ({ ...prev, [v]: !!c }))} className="h-3.5 w-3.5" />
            <Label htmlFor={`var-${v}`} className="text-[11px] cursor-pointer leading-none">{v}</Label>
          </div>
        ))}
        {(form.type === "image" || form.type === "video") && (
          <select value={form.aspect} onChange={(e) => update("aspect", e.target.value as Aspect)}
            className="ml-1 px-1.5 py-0.5 text-[11px] rounded border bg-background h-6">
            {ASPECTS.map(a => <option key={a} value={a}>{ASPECT_LABELS[a]} {a}</option>)}
          </select>
        )}
      </div>
      {/* UPLOAD IMAGEN REFERENCIA · solo type=image (UX-6) */}
      {form.type === "image" && (
        <div className="flex items-center gap-2">
          <label className="flex-1 text-[11px] cursor-pointer text-muted-foreground hover:text-foreground border border-dashed rounded px-2 py-1 text-center">
            📎 {form.reference_image_b64 ? "Referencia adjunta · click para cambiar" : "Adjuntar imagen referencia (opcional)"}
            <input type="file" accept="image/*" className="hidden" onChange={handleRefImageChange} />
          </label>
          {form.reference_image_b64 && (
            <button type="button" onClick={() => update("reference_image_b64", undefined)}
              className="text-xs text-red-500 hover:text-red-700 px-1" aria-label="Quitar referencia">✗</button>
          )}
        </div>
      )}
      {/* BOTÓN GENERAR */}
      <Button onClick={onGenerate} disabled={isPending || !form.topic.trim() || !hasVar}
        className="w-full gap-2 bg-green-600 hover:bg-green-700 text-white h-11">
        {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
        {isPending ? "Generando…" : "Generar con ARIA"}
      </Button>
    </div>
  );
}
