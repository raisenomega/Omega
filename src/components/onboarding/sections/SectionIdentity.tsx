import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { INDUSTRIES, REGIONS } from "@/lib/client-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionIdentity({ form }: Props) {
  const v = form.watch("identity");
  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <Label>Nombre del negocio *</Label>
        <Input value={v?.name ?? ""} onChange={(e) => form.setValue("identity.name", e.target.value, { shouldValidate: true })} maxLength={120} />
      </div>
      <div className="space-y-1">
        <Label>Industria *</Label>
        <Select value={v?.industry ?? ""} onValueChange={(x) => form.setValue("identity.industry", x as OnboardingForm["identity"]["industry"], { shouldValidate: true })}>
          <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
          <SelectContent>{INDUSTRIES.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent>
        </Select>
      </div>
      <div className="space-y-1">
        <Label>Región *</Label>
        <Select value={v?.region ?? ""} onValueChange={(x) => form.setValue("identity.region", x as OnboardingForm["identity"]["region"], { shouldValidate: true })}>
          <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
          <SelectContent>{REGIONS.map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
        </Select>
      </div>
    </div>
  );
}
