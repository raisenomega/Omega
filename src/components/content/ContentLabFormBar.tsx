import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PLATFORMS, PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { TYPES, TYPE_LABELS, TONES, TONE_LABELS } from "@/lib/content-lab-constants";
import type { FormState } from "./ContentLabFormV2";

interface Props {
  clientList: Array<{ id: string; name: string }>;
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  onResearch: () => void;
}

function Sel({ value, onChange, options, labels }: { value: string; onChange: (v: string) => void; options: readonly string[]; labels: Record<string, string> }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}
      className="px-2 py-1.5 text-sm rounded-md border bg-background flex-1 min-w-0">
      {options.map(o => <option key={o} value={o}>{labels[o] ?? o}</option>)}
    </select>
  );
}

export function ContentLabFormBar({ clientList, form, setForm, onResearch }: Props) {
  const update = <K extends keyof FormState>(k: K, v: FormState[K]) => setForm(prev => ({ ...prev, [k]: v }));
  return (
    <div className="flex flex-wrap md:flex-nowrap rounded-lg border overflow-hidden">
      <div className="bg-green-50 dark:bg-green-950/30 p-2 flex flex-wrap gap-2 items-center flex-1 min-w-0">
        <select value={form.clientId} onChange={(e) => update("clientId", e.target.value)}
          className="px-2 py-1.5 text-sm rounded-md border bg-background flex-1 min-w-[120px]">
          <option value="">— Cliente —</option>
          {clientList.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <Sel value={form.platform} onChange={(v) => update("platform", v)} options={PLATFORMS} labels={PLATFORM_LABELS} />
        <Sel value={form.type} onChange={(v) => update("type", v)} options={TYPES} labels={TYPE_LABELS} />
        <Sel value={form.tone} onChange={(v) => update("tone", v)} options={TONES} labels={TONE_LABELS} />
      </div>
      <div className="bg-blue-50 dark:bg-blue-950/30 p-2 flex gap-2 items-center flex-1 min-w-0">
        <Search className="h-4 w-4 text-blue-600 dark:text-blue-400 shrink-0" />
        <Input value={form.braveQuery} onChange={(e) => update("braveQuery", e.target.value)}
          placeholder="¿Qué querés que ARIA investigue?" className="flex-1 h-8 text-sm" />
        <Button size="sm" variant="outline" onClick={onResearch} className="h-8 text-xs">Research</Button>
      </div>
    </div>
  );
}
