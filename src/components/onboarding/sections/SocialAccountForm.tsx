import { Plus, Check } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { PLATFORMS, PLATFORM_LABELS, PUBLISHING_FREQUENCIES } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { PillGroup } from "../PillGroup";

type Acc = OnboardingForm["social_accounts"][number];

interface SocialAccountFormProps {
  value: Acc;
  onChange: <K extends keyof Acc>(field: K, x: Acc[K]) => void;
  onSubmit: () => void;
  isEditing: boolean;
}

// URL del perfil omitida (DEBT-040 · OAuth completará connection_metadata).
export function SocialAccountForm({ value, onChange, onSubmit, isEditing }: SocialAccountFormProps) {
  const canSubmit = !!value.platform && value.username.trim().length > 0;
  return (
    <div className="space-y-2.5">
      <div className="space-y-1"><Label className="text-xs">Plataforma</Label>
        <PillGroup
          options={PLATFORMS}
          labels={PLATFORM_LABELS}
          value={value.platform}
          onChange={(x) => onChange("platform", x as Acc["platform"])}
          cols={3}
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">@handle</Label>
          <Input className="h-8" placeholder="@usuario" value={value.username} onChange={(e) => onChange("username", e.target.value)} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Seguidores aprox.</Label>
          <Input className="h-8" type="number" min={0} value={value.approx_followers ?? ""} onChange={(e) => onChange("approx_followers", e.target.value ? Number(e.target.value) : null)} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-xs">Frecuencia</Label>
        <PillGroup
          options={PUBLISHING_FREQUENCIES}
          value={value.publishing_frequency ?? ""}
          onChange={(x) => onChange("publishing_frequency", x as Acc["publishing_frequency"])}
          cols={3}
        />
      </div>
      <div className="flex flex-wrap gap-3 text-xs pt-0.5">
        <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={value.is_primary} onCheckedChange={(c) => onChange("is_primary", c === true)} />Primaria</label>
        <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={value.is_business_account} onCheckedChange={(c) => onChange("is_business_account", c === true)} />Business</label>
        <label className="flex items-center gap-1 cursor-pointer"><Checkbox checked={value.auto_publish_allowed} onCheckedChange={(c) => onChange("auto_publish_allowed", c === true)} />Auto-publicar</label>
      </div>
      <Button onClick={onSubmit} disabled={!canSubmit} className="w-full gap-1 h-8" size="sm">
        {isEditing ? <><Check className="h-4 w-4" />Guardar cambios</> : <><Plus className="h-4 w-4" />Agregar cuenta</>}
      </Button>
    </div>
  );
}
