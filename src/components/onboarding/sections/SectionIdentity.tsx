import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { INDUSTRIES, type Region } from "@/lib/client-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { RegionsMultiSelect } from "./RegionsMultiSelect";
import { PillGroup } from "../PillGroup";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionIdentity({ form }: Props) {
  const v = form.watch("identity");
  const regions = (v?.regions ?? []) as Region[];

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
        <RegionsMultiSelect
          value={regions}
          onChange={(next) => form.setValue("identity.regions", next, { shouldValidate: true })}
        />
      </div>
    </div>
  );
}
