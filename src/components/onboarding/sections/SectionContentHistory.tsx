import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionContentHistory({ form }: Props) {
  const v = form.watch("content_history");
  const set = <K extends keyof OnboardingForm["content_history"]>(k: K, x: OnboardingForm["content_history"][K]) => form.setValue(`content_history.${k}`, x);
  return (
    <div className="space-y-3">
      <label className="flex items-center gap-2 text-sm cursor-pointer">
        <Checkbox checked={!!v?.has_existing_content} onCheckedChange={(c) => set("has_existing_content", c === true)} />
        Ya tengo contenido publicado
      </label>
      <div className="space-y-1"><Label>Seguidores aproximados (total)</Label>
        <Input type="number" min={0} value={v?.existing_followers ?? ""} onChange={(e) => set("existing_followers", e.target.value ? Number(e.target.value) : null)} /></div>
      <div className="space-y-1"><Label>URL de tu mejor post</Label>
        <Input value={v?.best_post_url ?? ""} onChange={(e) => set("best_post_url", e.target.value)} placeholder="https://..." /></div>
      <div className="space-y-1"><Label>¿Qué funcionó?</Label>
        <Textarea value={v?.what_worked ?? ""} onChange={(e) => set("what_worked", e.target.value)} rows={2} /></div>
      <div className="space-y-1"><Label>¿Qué falló?</Label>
        <Textarea value={v?.what_failed ?? ""} onChange={(e) => set("what_failed", e.target.value)} rows={2} /></div>
      <div className="space-y-1"><Label>Temas recurrentes (separados por coma)</Label>
        <Input value={(v?.content_themes ?? []).join(", ")} onChange={(e) => set("content_themes", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} /></div>
    </div>
  );
}
