import { Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

export const VARIATIONS = ["Conservadora", "Balanceada", "Atrevida"] as const;
export type VariationLabel = typeof VARIATIONS[number];

export interface FormState {
  platform: string; type: string; tone: string; topic: string; braveQuery: string; clientId: string;
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

  return (
    <div className="space-y-3 h-full flex flex-col">
      {/* CAJÓN AMARILLO · Prompt principal (flex-1 ocupa altura disponible) */}
      <div className="bg-background border-2 border-amber-500 rounded-lg p-3 flex-1 flex flex-col">
        <Textarea value={form.topic} onChange={(e) => update("topic", e.target.value)}
          className="bg-transparent border-none outline-none resize-none w-full h-full focus:ring-0 focus-visible:ring-0 flex-1 min-h-[120px]" />
      </div>
      {/* CHECKBOXES VARIACIONES · flex-wrap para columna estrecha */}
      <div className="flex flex-wrap gap-3 items-center justify-center py-1">
        {VARIATIONS.map(v => (
          <div key={v} className="flex items-center gap-1.5">
            <Checkbox id={`var-${v}`} checked={variations[v]} onCheckedChange={(c) => setVariations(prev => ({ ...prev, [v]: !!c }))} />
            <Label htmlFor={`var-${v}`} className="text-xs cursor-pointer">{v}</Label>
          </div>
        ))}
      </div>
      {/* BOTÓN GENERAR */}
      <Button onClick={onGenerate} disabled={isPending || !form.topic.trim() || !hasVar}
        className="w-full gap-2 bg-green-600 hover:bg-green-700 text-white h-11">
        {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
        {isPending ? "Generando…" : "Generar con ARIA"}
      </Button>
    </div>
  );
}
