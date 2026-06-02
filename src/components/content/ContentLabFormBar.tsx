import { Search, Video } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PLATFORMS, PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { TYPES, TYPE_LABELS, TONES, TONE_LABELS } from "@/lib/content-lab-constants";
import { useMyAccounts } from "@/hooks/useMyAccounts";
import type { FormState } from "./ContentLabFormV2";

interface Props {
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  onResearch: () => void;
}

function Sel({ value, onChange, options, labels }: { value: string; onChange: (v: string) => void; options: readonly string[]; labels: Record<string, string> }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}
      className="px-2 py-1 text-sm rounded-md border bg-background min-w-0 w-[110px] flex-none">
      {options.map(o => <option key={o} value={o}>{labels[o] ?? o}</option>)}
    </select>
  );
}

export function ContentLabFormBar({ form, setForm, onResearch }: Props) {
  const navigate = useNavigate();
  const update = <K extends keyof FormState>(k: K, v: FormState[K]) => setForm(prev => ({ ...prev, [k]: v }));
  const { data: accounts = [] } = useMyAccounts(form.clientId, form.platform);
  return (
    <div className="flex flex-wrap items-center gap-2 px-3 py-2 border-2 border-green-500 rounded-lg bg-card/80 backdrop-blur-sm">
      <Sel value={form.platform} onChange={(v) => update("platform", v)} options={PLATFORMS} labels={PLATFORM_LABELS} />
      {accounts.length > 1 && (
        <select value={form.accountId} onChange={(e) => update("accountId", e.target.value)}
          className="px-2 py-1 text-sm rounded-md border bg-background min-w-0 w-[140px] flex-none"
          title="Elegir cuenta específica (cliente tiene varias en esta plataforma)">
          <option value="">— Cuenta —</option>
          {accounts.map(a => <option key={a.id} value={a.id}>{a.account_name}</option>)}
        </select>
      )}
      <Sel value={form.type} onChange={(v) => update("type", v)} options={TYPES} labels={TYPE_LABELS} />
      {form.type === "video" && (
        <Button size="sm" variant="outline" onClick={() => navigate("/add-ons", { state: { scrollTo: "video-packs" } })}
          className="gap-1 h-8 text-xs animate-pulse border-amber-500 text-amber-600 hover:bg-amber-50 hover:text-amber-700">
          <Video className="h-3.5 w-3.5" />
          Video Packs
        </Button>
      )}
      <Sel value={form.tone} onChange={(v) => update("tone", v)} options={TONES} labels={TONE_LABELS} />
      <div className="h-6 w-px bg-border/60 hidden sm:block" aria-hidden />
      <Input value={form.braveQuery} onChange={(e) => update("braveQuery", e.target.value)}
        placeholder="¿Qué querés que ARIA investigue?" className="flex-1 h-8 text-sm min-w-[240px]" />
      <Button size="sm" onClick={onResearch}
        className="bg-green-600 hover:bg-green-700 text-white font-semibold gap-1.5 h-8 text-xs px-4 rounded-md">
        <Search className="h-3.5 w-3.5" />
        Research
      </Button>
    </div>
  );
}
