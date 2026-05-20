import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2 } from "lucide-react";
import { PLATFORMS, PLATFORM_LABELS, PUBLISHING_FREQUENCIES } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }
type Acc = OnboardingForm["social_accounts"][number];

const EMPTY: Acc = { platform: "instagram", username: "", profile_url: null, is_primary: false, auto_publish_allowed: false, approx_followers: null, publishing_frequency: null, is_business_account: false };

export function SectionSocialAccounts({ form }: Props) {
  const list = form.watch("social_accounts") ?? [];
  const update = (i: number, patch: Partial<Acc>) => { const next = [...list]; next[i] = { ...next[i], ...patch }; form.setValue("social_accounts", next); };
  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground bg-muted/40 px-3 py-2 rounded">
        Por ahora capturamos tu @handle. Conectaremos tu cuenta vía OAuth en próximos días para publicar directo desde OMEGA.
      </p>
      {list.map((acc, i) => (
        <div key={i} className="border border-border rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between"><Label className="text-sm">Cuenta #{i + 1}</Label>
            <Button size="icon" variant="ghost" onClick={() => form.setValue("social_accounts", list.filter((_, j) => j !== i))}><Trash2 className="h-4 w-4" /></Button></div>
          <div className="grid grid-cols-2 gap-2">
            <Select value={acc.platform} onValueChange={(x) => update(i, { platform: x as Acc["platform"] })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{PLATFORMS.map((p) => <SelectItem key={p} value={p}>{PLATFORM_LABELS[p]}</SelectItem>)}</SelectContent>
            </Select>
            <Input placeholder="@handle" value={acc.username} onChange={(e) => update(i, { username: e.target.value })} />
          </div>
          <Input placeholder="URL del perfil (opcional)" value={acc.profile_url ?? ""} onChange={(e) => update(i, { profile_url: e.target.value })} />
          <div className="grid grid-cols-2 gap-2">
            <Input type="number" min={0} placeholder="Seguidores aprox." value={acc.approx_followers ?? ""} onChange={(e) => update(i, { approx_followers: e.target.value ? Number(e.target.value) : null })} />
            <Select value={acc.publishing_frequency ?? ""} onValueChange={(x) => update(i, { publishing_frequency: x as Acc["publishing_frequency"] })}>
              <SelectTrigger><SelectValue placeholder="Frecuencia" /></SelectTrigger>
              <SelectContent>{PUBLISHING_FREQUENCIES.map((f) => <SelectItem key={f} value={f}>{f}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="flex flex-wrap gap-3 text-xs">
            <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={acc.is_primary} onCheckedChange={(c) => update(i, { is_primary: c === true })} />Primaria</label>
            <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={acc.is_business_account} onCheckedChange={(c) => update(i, { is_business_account: c === true })} />Business</label>
            <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={acc.auto_publish_allowed} onCheckedChange={(c) => update(i, { auto_publish_allowed: c === true })} />Auto-publicar (futuro)</label>
          </div>
        </div>
      ))}
      <Button size="sm" variant="outline" onClick={() => form.setValue("social_accounts", [...list, EMPTY])}>+ Agregar cuenta</Button>
    </div>
  );
}
