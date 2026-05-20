import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2 } from "lucide-react";
import { AUDIENCE_AGE_RANGES, GENDERS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionAudience({ form }: Props) {
  const v = form.watch("audience");
  const competitors = v?.competitors ?? [];
  return (
    <div className="space-y-3">
      <div className="space-y-1"><Label>Audiencia objetivo</Label>
        <Textarea value={v?.target_audience ?? ""} onChange={(e) => form.setValue("audience.target_audience", e.target.value)} rows={2} /></div>
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1"><Label>Rango de edad</Label>
          <Select value={v?.audience_age_range ?? ""} onValueChange={(x) => form.setValue("audience.audience_age_range", x as OnboardingForm["audience"]["audience_age_range"])}>
            <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{AUDIENCE_AGE_RANGES.map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="space-y-1"><Label>Género</Label>
          <Select value={v?.audience_gender ?? ""} onValueChange={(x) => form.setValue("audience.audience_gender", x as OnboardingForm["audience"]["audience_gender"])}>
            <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{GENDERS.map((g) => <SelectItem key={g} value={g}>{g}</SelectItem>)}</SelectContent>
          </Select>
        </div>
      </div>
      <div className="space-y-2">
        <Label>Competidores</Label>
        {competitors.map((c, i) => (
          <div key={i} className="flex gap-2">
            <Input placeholder="Nombre" value={c.name} onChange={(e) => { const next = [...competitors]; next[i] = { ...c, name: e.target.value }; form.setValue("audience.competitors", next); }} />
            <Input placeholder="URL (opcional)" value={c.url ?? ""} onChange={(e) => { const next = [...competitors]; next[i] = { ...c, url: e.target.value }; form.setValue("audience.competitors", next); }} />
            <Button size="icon" variant="ghost" onClick={() => form.setValue("audience.competitors", competitors.filter((_, j) => j !== i))}><Trash2 className="h-4 w-4" /></Button>
          </div>
        ))}
        <Button size="sm" variant="outline" onClick={() => form.setValue("audience.competitors", [...competitors, { name: "", url: null }])}>+ Agregar</Button>
      </div>
    </div>
  );
}
