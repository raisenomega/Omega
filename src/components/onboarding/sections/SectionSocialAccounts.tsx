import { useState } from "react";
import type { UseFormReturn } from "react-hook-form";
import { SocialAccountForm } from "./SocialAccountForm";
import { SocialAccountList } from "./SocialAccountList";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }
type Acc = OnboardingForm["social_accounts"][number];

const EMPTY: Acc = {
  platform: "instagram", username: "", profile_url: null,
  is_primary: false, auto_publish_allowed: false,
  approx_followers: null, publishing_frequency: null,
  is_business_account: false, is_paused: false,
};

export function SectionSocialAccounts({ form }: Props) {
  const list = form.watch("social_accounts") ?? [];
  const [draft, setDraft] = useState<Acc>(EMPTY);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const updateDraft = <K extends keyof Acc>(k: K, x: Acc[K]) => setDraft((d) => ({ ...d, [k]: x }));

  const handleSubmit = () => {
    const next = [...list];
    if (editingIndex !== null) next[editingIndex] = draft;
    else next.push(draft);
    form.setValue("social_accounts", next);
    setDraft(EMPTY);
    setEditingIndex(null);
  };

  const handleEdit = (i: number) => { setDraft(list[i]); setEditingIndex(i); };
  const handleTogglePause = (i: number) => {
    const next = [...list]; next[i] = { ...next[i], is_paused: !next[i].is_paused };
    form.setValue("social_accounts", next);
  };
  const handleRemove = (i: number) => {
    form.setValue("social_accounts", list.filter((_, j) => j !== i));
    if (editingIndex === i) { setDraft(EMPTY); setEditingIndex(null); }
  };

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted-foreground bg-muted/40 px-3 py-2 rounded">
        Por ahora capturamos tu @handle. Conectaremos tu cuenta vía OAuth en próximos días para publicar directo desde OMEGA.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium mb-2">{editingIndex !== null ? "Editar cuenta" : "Nueva cuenta"}</h4>
          <SocialAccountForm value={draft} onChange={updateDraft} onSubmit={handleSubmit} isEditing={editingIndex !== null} />
        </div>
        <div>
          <h4 className="text-sm font-medium mb-2">Cuentas agregadas ({list.length})</h4>
          <SocialAccountList accounts={list} onEdit={handleEdit} onTogglePause={handleTogglePause} onRemove={handleRemove} />
        </div>
      </div>
    </div>
  );
}
