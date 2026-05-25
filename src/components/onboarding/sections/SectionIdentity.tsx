import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { INDUSTRIES, REGIONS } from "@/lib/client-constants";
import { REGION_LABELS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { PillGroup } from "../PillGroup";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionIdentity({ form }: Props) {
  const v = form.watch("identity");

  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <Label className="text-xs">Nombre del negocio *</Label>
        <Input
          className="h-8"
          value={v?.name ?? ""}
          onChange={(e) => form.setValue("identity.name", e.target.value, { shouldValidate: true })}
          maxLength={120}
        />
      </div>
      <div className="space-y-1">
        <Label className="text-xs">Industria *</Label>
        <PillGroup
          options={INDUSTRIES}
          value={v?.industry ?? ""}
          onChange={(x) => form.setValue("identity.industry", x as OnboardingForm["identity"]["industry"], { shouldValidate: true })}
          cols={4}
        />
      </div>
      <div className="space-y-1">
        <Label className="text-xs">Regiones * (multi-selección)</Label>
        <PillGroup
          options={REGIONS}
          labels={REGION_LABELS}
          value={v?.regions ?? []}
          onChange={(x) => form.setValue("identity.regions", x as string[], { shouldValidate: true })}
          multi
          cols={4}
        />
      </div>
      {/* Campos opcionales · sin placeholder (P1: cero texto sugerido) */}
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <Label className="text-xs">Sitio web del negocio</Label>
          <Input className="h-8" value={v?.website ?? ""} onChange={(e) => form.setValue("identity.website", e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Email de contacto</Label>
          <Input className="h-8" value={v?.business_email ?? ""} onChange={(e) => form.setValue("identity.business_email", e.target.value)} />
        </div>
      </div>
    </div>
  );
}
