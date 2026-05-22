import { Search, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { PLATFORMS, PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { TYPES, TYPE_LABELS, TONES, TONE_LABELS } from "@/lib/content-lab-constants";

export const VARIATIONS = ["Conservadora", "Balanceada", "Atrevida"] as const;
export type VariationLabel = typeof VARIATIONS[number];

export interface FormState {
  platform: string; type: string; tone: string; topic: string; braveQuery: string; clientId: string;
}

interface Props {
  clientList: Array<{ id: string; name: string }>;
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  variations: Record<VariationLabel, boolean>;
  setVariations: React.Dispatch<React.SetStateAction<Record<VariationLabel, boolean>>>;
  onGenerate: () => void;
  onResearch: () => void;
  isPending?: boolean;
}

function Select({ value, onChange, options, labels }: { value: string; onChange: (v: string) => void; options: readonly string[]; labels: Record<string, string> }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}
      className="px-2 py-1.5 text-sm rounded-md border bg-background flex-1 min-w-0">
      {options.map(o => <option key={o} value={o}>{labels[o] ?? o}</option>)}
    </select>
  );
}

export function ContentLabFormV2({ clientList, form, setForm, variations, setVariations, onGenerate, onResearch, isPending }: Props) {
  const update = <K extends keyof FormState>(k: K, v: FormState[K]) => setForm(prev => ({ ...prev, [k]: v }));
  const hasVar = Object.values(variations).some(Boolean);

  return (
    <div className="space-y-3">
      {/* BARRA UNIFICADA · Verde (form) | Azul (research) · duotone edge-to-edge */}
      <div className="flex flex-wrap md:flex-nowrap">
        <div className="bg-green-50 dark:bg-green-950/30 p-3 flex flex-wrap gap-2 items-center flex-1 min-w-0">
          <select value={form.clientId} onChange={(e) => update("clientId", e.target.value)}
            className="px-2 py-1.5 text-sm rounded-md border bg-background flex-1 min-w-[140px]">
            <option value="">— Cliente —</option>
            {clientList.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <Select value={form.platform} onChange={(v) => update("platform", v)} options={PLATFORMS} labels={PLATFORM_LABELS} />
          <Select value={form.type} onChange={(v) => update("type", v)} options={TYPES} labels={TYPE_LABELS} />
          <Select value={form.tone} onChange={(v) => update("tone", v)} options={TONES} labels={TONE_LABELS} />
        </div>
        <div className="bg-blue-50 dark:bg-blue-950/30 p-3 flex gap-2 items-center flex-1 min-w-0">
          <Search className="h-4 w-4 text-blue-600 dark:text-blue-400 shrink-0" />
          <Input value={form.braveQuery} onChange={(e) => update("braveQuery", e.target.value)}
            placeholder="¿Qué querés que ARIA investigue antes de generar?" className="flex-1 h-8 text-sm" />
          <Button size="sm" variant="outline" onClick={onResearch} className="h-8 text-xs">Research</Button>
        </div>
      </div>
      {/* CAJÓN AMARILLO · Prompt principal */}
      <div className="bg-amber-50 dark:bg-amber-950/30 border-2 border-amber-500 dark:border-amber-600 rounded-lg p-3">
        <Label className="text-xs font-semibold text-amber-900 dark:text-amber-200">Prompt principal</Label>
        <Textarea value={form.topic} onChange={(e) => update("topic", e.target.value)} rows={6}
          placeholder="Describe el contenido · qué quiere comunicar · audiencia · CTA esperado"
          className="mt-2 resize-none bg-background border-amber-300 dark:border-amber-700" />
      </div>
      {/* CHECKBOXES VARIACIONES (no toggle) */}
      <div className="flex gap-4 items-center justify-center py-2">
        {VARIATIONS.map(v => (
          <div key={v} className="flex items-center gap-2">
            <Checkbox id={`var-${v}`} checked={variations[v]} onCheckedChange={(c) => setVariations(prev => ({ ...prev, [v]: !!c }))} />
            <Label htmlFor={`var-${v}`} className="text-sm cursor-pointer">{v}</Label>
          </div>
        ))}
      </div>
      {/* BOTÓN GENERAR */}
      <Button onClick={onGenerate} disabled={isPending || !form.topic.trim() || !hasVar}
        className="w-full gap-2 bg-amber-500 hover:bg-amber-600 text-white h-11">
        {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
        {isPending ? "Generando…" : "Generar con ARIA"}
      </Button>
    </div>
  );
}
