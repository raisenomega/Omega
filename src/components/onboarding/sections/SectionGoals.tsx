import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PRIMARY_GOALS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionGoals({ form }: Props) {
  const v = form.watch("goals");
  const set = <K extends keyof OnboardingForm["goals"]>(k: K, x: OnboardingForm["goals"][K]) => form.setValue(`goals.${k}`, x);
  return (
    <div className="space-y-3">
      <div className="space-y-1"><Label>Objetivo principal</Label>
        <Select value={v?.primary_goal ?? ""} onValueChange={(x) => set("primary_goal", x as OnboardingForm["goals"]["primary_goal"])}>
          <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
          <SelectContent>{PRIMARY_GOALS.map((g) => <SelectItem key={g} value={g}>{g}</SelectItem>)}</SelectContent>
        </Select></div>
      <div className="space-y-1"><Label>Meta este mes</Label>
        <Textarea value={v?.goal_this_month ?? ""} onChange={(e) => set("goal_this_month", e.target.value)} rows={2} /></div>
      <div className="space-y-1"><Label>Meta este trimestre</Label>
        <Textarea value={v?.goal_this_quarter ?? ""} onChange={(e) => set("goal_this_quarter", e.target.value)} rows={2} /></div>
      <div className="space-y-1"><Label>Prioridad ahora</Label>
        <Input value={v?.goal_priority_now ?? ""} onChange={(e) => set("goal_priority_now", e.target.value)} /></div>
      <div className="space-y-1"><Label>Métrica de éxito</Label>
        <Input value={v?.success_metric ?? ""} onChange={(e) => set("success_metric", e.target.value)} /></div>
      <div className="space-y-1"><Label>Revenue target mensual (USD)</Label>
        <Input type="number" min={0} step="0.01" value={v?.monthly_revenue_target ?? ""} onChange={(e) => set("monthly_revenue_target", e.target.value ? Number(e.target.value) : null)} /></div>
    </div>
  );
}
