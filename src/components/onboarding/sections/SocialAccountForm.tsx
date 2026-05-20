import { Plus, Check } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PLATFORMS, PLATFORM_LABELS, PUBLISHING_FREQUENCIES } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

type Acc = OnboardingForm["social_accounts"][number];

interface SocialAccountFormProps {
  value: Acc;
  onChange: <K extends keyof Acc>(field: K, x: Acc[K]) => void;
  onSubmit: () => void;
  isEditing: boolean;
}

export function SocialAccountForm({ value, onChange, onSubmit, isEditing }: SocialAccountFormProps) {
  const canSubmit = !!value.platform && value.username.trim().length > 0;
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-sm">Plataforma</Label>
          <Select value={value.platform} onValueChange={(x) => onChange("platform", x as Acc["platform"])}>
            <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
            <SelectContent>{PLATFORMS.map((p) => <SelectItem key={p} value={p}>{PLATFORM_LABELS[p]}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="space-y-1"><Label className="text-sm">@handle</Label>
          <Input className="h-9" placeholder="@usuario" value={value.username} onChange={(e) => onChange("username", e.target.value)} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-sm">URL del perfil</Label>
        <Input className="h-9" placeholder="https://..." value={value.profile_url ?? ""} onChange={(e) => onChange("profile_url", e.target.value)} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-sm">Seguidores aprox.</Label>
          <Input className="h-9" type="number" min={0} value={value.approx_followers ?? ""} onChange={(e) => onChange("approx_followers", e.target.value ? Number(e.target.value) : null)} />
        </div>
        <div className="space-y-1"><Label className="text-sm">Frecuencia</Label>
          <Select value={value.publishing_frequency ?? ""} onValueChange={(x) => onChange("publishing_frequency", x as Acc["publishing_frequency"])}>
            <SelectTrigger className="h-9"><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{PUBLISHING_FREQUENCIES.map((f) => <SelectItem key={f} value={f}>{f}</SelectItem>)}</SelectContent>
          </Select>
        </div>
      </div>
      <div className="flex flex-wrap gap-3 text-xs pt-1">
        <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={value.is_primary} onCheckedChange={(c) => onChange("is_primary", c === true)} />Primaria</label>
        <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={value.is_business_account} onCheckedChange={(c) => onChange("is_business_account", c === true)} />Business</label>
        <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={value.auto_publish_allowed} onCheckedChange={(c) => onChange("auto_publish_allowed", c === true)} />Auto-publicar</label>
      </div>
      <Button onClick={onSubmit} disabled={!canSubmit} className="w-full gap-1" size="sm">
        {isEditing ? <><Check className="h-4 w-4" />Guardar cambios</> : <><Plus className="h-4 w-4" />Agregar cuenta</>}
      </Button>
    </div>
  );
}
