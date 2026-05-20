import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import { AUDIENCE_AGE_RANGES, GENDERS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { PillGroup } from "../PillGroup";

interface Props { form: UseFormReturn<OnboardingForm> }

const GENDER_LABELS = { male: "Hombres", female: "Mujeres", mixed: "Mixto", non_binary: "No binario", any: "Cualquiera" };

export function SectionAudience({ form }: Props) {
  const v = form.watch("audience");
  const competitors = v?.competitors ?? [];
  const setComp = (next: typeof competitors) => form.setValue("audience.competitors", next);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="space-y-3">
        <div className="space-y-1"><Label className="text-xs">Audiencia objetivo</Label>
          <Textarea value={v?.target_audience ?? ""} onChange={(e) => form.setValue("audience.target_audience", e.target.value)} rows={2} className="resize-none" /></div>
        <div className="space-y-1"><Label className="text-xs">Rango de edad</Label>
          <PillGroup
            options={AUDIENCE_AGE_RANGES}
            value={v?.audience_age_range ?? ""}
            onChange={(x) => form.setValue("audience.audience_age_range", x as OnboardingForm["audience"]["audience_age_range"])}
            cols={4}
          />
        </div>
        <div className="space-y-1"><Label className="text-xs">Género</Label>
          <PillGroup
            options={GENDERS}
            labels={GENDER_LABELS}
            value={v?.audience_gender ?? ""}
            onChange={(x) => form.setValue("audience.audience_gender", x as OnboardingForm["audience"]["audience_gender"])}
            cols={3}
          />
        </div>
      </div>
      <div className="space-y-2">
        <h4 className="text-sm font-medium">Competidores ({competitors.length})</h4>
        <div className="space-y-1.5 max-h-[260px] overflow-y-auto pr-1">
          {competitors.map((c, i) => (
            <div key={i} className="flex gap-1.5">
              <Input className="h-8" placeholder="Nombre" value={c.name} onChange={(e) => { const n = [...competitors]; n[i] = { ...c, name: e.target.value }; setComp(n); }} />
              <Input className="h-8" placeholder="URL" value={c.url ?? ""} onChange={(e) => { const n = [...competitors]; n[i] = { ...c, url: e.target.value }; setComp(n); }} />
              <Button size="icon" variant="ghost" className="h-8 w-8 shrink-0" onClick={() => setComp(competitors.filter((_, j) => j !== i))}><Trash2 className="h-3.5 w-3.5" /></Button>
            </div>
          ))}
        </div>
        <Button size="sm" variant="outline" className="gap-1 w-full h-8" onClick={() => setComp([...competitors, { name: "", url: null }])}>
          <Plus className="h-3.5 w-3.5" />Agregar competidor
        </Button>
      </div>
    </div>
  );
}
