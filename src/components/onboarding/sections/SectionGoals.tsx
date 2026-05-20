import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PRIMARY_GOALS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { PillGroup } from "../PillGroup";

interface Props { form: UseFormReturn<OnboardingForm> }

const GOAL_LABELS = { awareness: "Awareness", leads: "Leads", sales: "Ventas", community: "Comunidad", retention: "Retención" };

export function SectionGoals({ form }: Props) {
  const v = form.watch("goals");
  const set = <K extends keyof OnboardingForm["goals"]>(k: K, x: OnboardingForm["goals"][K]) => form.setValue(`goals.${k}`, x);
  return (
    <div className="space-y-3">
      <div className="space-y-1"><Label className="text-xs">Objetivo principal</Label>
        <PillGroup
          options={PRIMARY_GOALS}
          labels={GOAL_LABELS}
          value={v?.primary_goal ?? ""}
          onChange={(x) => set("primary_goal", x as OnboardingForm["goals"]["primary_goal"])}
          cols={5}
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Métrica de éxito</Label>
          <Input className="h-8" value={v?.success_metric ?? ""} onChange={(e) => set("success_metric", e.target.value)} placeholder="ej. 30 leads/mes" />
        </div>
        <div className="space-y-1"><Label className="text-xs">Prioridad ahora</Label>
          <Input className="h-8" value={v?.goal_priority_now ?? ""} onChange={(e) => set("goal_priority_now", e.target.value)} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Meta este mes</Label>
          <Input className="h-8" placeholder="ej: Conseguir 50 nuevos seguidores"
            value={v?.goal_this_month ?? ""} onChange={(e) => set("goal_this_month", e.target.value)} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Meta este trimestre</Label>
          <Input className="h-8" placeholder="ej: Lanzar 1 campaña paga"
            value={v?.goal_this_quarter ?? ""} onChange={(e) => set("goal_this_quarter", e.target.value)} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-xs">Target revenue mensual (USD)</Label>
        <Input className="h-8" type="number" min={0} step="0.01" value={v?.monthly_revenue_target ?? ""} onChange={(e) => set("monthly_revenue_target", e.target.value ? Number(e.target.value) : null)} />
      </div>
    </div>
  );
}
