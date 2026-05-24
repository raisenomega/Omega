import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useImprovePrompt } from "@/hooks/useImprovePrompt";
import { ImprovePromptPanel } from "./ImprovePromptPanel";
import { AspectRow } from "./AspectRow";
import { PromptAttachmentControls } from "./PromptAttachmentControls";
import type { Aspect } from "./_aspect";

export const VARIATIONS = ["Conservadora", "Balanceada", "Atrevida"] as const;
export type VariationLabel = typeof VARIATIONS[number];
export { ASPECTS, type Aspect } from "./_aspect";  // back-compat re-export

export interface FormState {
  platform: string; type: string; tone: string; topic: string; braveQuery: string; clientId: string;
  aspect: Aspect;
  reference_image_b64?: string;          // UX-6 · imagen de referencia
  reference_attachment_b64?: string;     // DEBT-CL-020 · PDF/DOCX/MD/TXT
  reference_mime_type?: string;          // DEBT-CL-020 · MIME del attachment
  accountId: string;  // DEBT-CL-015 · vacío = backend resuelve primera activa
}

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

  return (
    <div className="space-y-3 h-full flex flex-col">
      {improvedText && (
        <ImprovePromptPanel improvedText={improvedText}
          onAccept={() => { update("topic", improvedText); setImprovedText(null); }}
          onReject={() => setImprovedText(null)} />
      )}
      {/* CAJÓN AMARILLO · Prompt + 📎 left (type=image) + ✨ Mejorar right */}
      <div className="bg-background border-2 border-amber-500 rounded-lg p-3 flex-1 flex flex-col relative">
        <Textarea value={form.topic} onChange={(e) => update("topic", e.target.value)}
          className="bg-transparent border-none outline-none resize-none w-full h-full focus:ring-0 focus-visible:ring-0 flex-1 min-h-[120px] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden" />
        <PromptAttachmentControls
          reference_image_b64={form.reference_image_b64}
          reference_attachment_b64={form.reference_attachment_b64}
          reference_mime_type={form.reference_mime_type}
          onImageChange={(b64) => update("reference_image_b64", b64)}
          onAttachmentChange={(b64, mime) => setForm(prev => ({ ...prev, reference_attachment_b64: b64, reference_mime_type: mime }))} />
        <Button size="sm" variant="ghost" onClick={handleImprove}
          disabled={!form.topic.trim() || improve.isPending}
          className="absolute bottom-2 right-2 h-7 text-[11px] gap-1 text-amber-700 hover:bg-amber-100 dark:hover:bg-amber-950/30">
          {improve.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
          Mejorar
        </Button>
      </div>
      {/* LÍNEA 1 · VARIACIONES (siempre · UX-4) */}
      <div className="flex flex-nowrap gap-2 items-center justify-center py-1">
        {VARIATIONS.map(v => (
          <div key={v} className="flex items-center gap-1">
            <Checkbox id={`var-${v}`} checked={variations[v]} onCheckedChange={(c) => setVariations(prev => ({ ...prev, [v]: !!c }))} className="h-3.5 w-3.5" />
            <Label htmlFor={`var-${v}`} className="text-[11px] cursor-pointer leading-none">{v}</Label>
          </div>
        ))}
      </div>
      {/* LÍNEA 2 · ASPECT toggle buttons (solo image/video · UX-3) */}
      {(form.type === "image" || form.type === "video") && (
        <AspectRow aspect={form.aspect} onChange={(a) => update("aspect", a)} />
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
