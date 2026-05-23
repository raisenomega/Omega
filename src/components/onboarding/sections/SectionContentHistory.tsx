import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionContentHistory({ form }: Props) {
  const v = form.watch("content_history");
  const set = <K extends keyof OnboardingForm["content_history"]>(k: K, x: OnboardingForm["content_history"][K]) => form.setValue(`content_history.${k}`, x);
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 items-end">
        <label className="flex items-center gap-2 text-xs cursor-pointer h-8">
          <Checkbox checked={!!v?.has_existing_content} onCheckedChange={(c) => set("has_existing_content", c === true)} />
          Ya tengo contenido publicado
        </label>
        <div className="space-y-1"><Label className="text-xs">Seguidores aprox.</Label>
          <Input className="h-8" type="number" min={0} value={v?.existing_followers ?? ""} onChange={(e) => set("existing_followers", e.target.value ? Number(e.target.value) : null)} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-xs">URL mejor post</Label>
        <Input className="h-8" value={v?.best_post_url ?? ""} onChange={(e) => set("best_post_url", e.target.value)} placeholder="https://..." />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">¿Qué funcionó?</Label>
          <Input className="h-8" placeholder="ej: Videos cortos con humor"
            value={v?.what_worked ?? ""} onChange={(e) => set("what_worked", e.target.value)} />
        </div>
        <div className="space-y-1"><Label className="text-xs">¿Qué falló?</Label>
          <Input className="h-8" placeholder="ej: Posts muy formales"
            value={v?.what_failed ?? ""} onChange={(e) => set("what_failed", e.target.value)} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-xs">Temas recurrentes (coma)</Label>
        <Input className="h-8" defaultValue={(v?.content_themes ?? []).join(", ")} onBlur={(e) => set("content_themes", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} placeholder="café, comunidad, recetas" key={(v?.content_themes ?? []).join("|")} />
      </div>
    </div>
  );
}
