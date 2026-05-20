import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BUSINESS_SIZES } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionBusiness({ form }: Props) {
  const v = form.watch("business");
  const set = <K extends keyof OnboardingForm["business"]>(k: K, x: OnboardingForm["business"][K]) => form.setValue(`business.${k}`, x);
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1"><Label>Nicho</Label><Input value={v?.niche ?? ""} onChange={(e) => set("niche", e.target.value)} /></div>
        <div className="space-y-1"><Label>Vertical</Label><Input value={v?.vertical ?? ""} onChange={(e) => set("vertical", e.target.value)} /></div>
      </div>
      <div className="space-y-1"><Label>¿Qué vende tu negocio?</Label>
        <Textarea value={v?.business_what ?? ""} onChange={(e) => set("business_what", e.target.value)} rows={2} /></div>
      <div className="space-y-1"><Label>¿A quién?</Label>
        <Textarea value={v?.business_to_whom ?? ""} onChange={(e) => set("business_to_whom", e.target.value)} rows={2} /></div>
      <div className="space-y-1"><Label>¿Qué te diferencia?</Label>
        <Textarea value={v?.business_diff ?? ""} onChange={(e) => set("business_diff", e.target.value)} rows={2} /></div>
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1"><Label>Tamaño</Label>
          <Select value={v?.business_size ?? ""} onValueChange={(x) => set("business_size", x as OnboardingForm["business"]["business_size"])}>
            <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{BUSINESS_SIZES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="space-y-1"><Label>Años operando</Label>
          <Input type="number" min={0} value={v?.years_operating ?? ""} onChange={(e) => set("years_operating", e.target.value ? Number(e.target.value) : null)} /></div>
      </div>
    </div>
  );
}
