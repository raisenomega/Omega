import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { INDUSTRIES, type Region } from "@/lib/client-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { RegionsMultiSelect } from "./RegionsMultiSelect";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionIdentity({ form }: Props) {
  const v = form.watch("identity");
  const regions = (v?.regions ?? []) as Region[];

  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <Label>Nombre del negocio *</Label>
        <Input
          value={v?.name ?? ""}
          onChange={(e) => form.setValue("identity.name", e.target.value, { shouldValidate: true })}
          maxLength={120}
        />
      </div>
      <div className="space-y-1">
        <Label>Industria *</Label>
        <Select
          value={v?.industry ?? ""}
          onValueChange={(x) => form.setValue("identity.industry", x as OnboardingForm["identity"]["industry"], { shouldValidate: true })}
        >
          <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
          <SelectContent>{INDUSTRIES.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent>
        </Select>
      </div>
      <div className="space-y-1">
        <Label>Regiones * (multi-selección)</Label>
        <RegionsMultiSelect
          value={regions}
          onChange={(next) => form.setValue("identity.regions", next, { shouldValidate: true })}
        />
      </div>
    </div>
  );
}
