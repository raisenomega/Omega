import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionInstructions({ form }: Props) {
  const v = form.watch("instructions");
  const set = <K extends keyof OnboardingForm["instructions"]>(k: K, x: OnboardingForm["instructions"][K]) => form.setValue(`instructions.${k}`, x);
  const hours = v?.preferred_publishing_hours ?? [];
  return (
    <div className="space-y-3">
      <div className="space-y-1"><Label className="text-xs">Instrucciones personalizadas</Label>
        <Textarea value={v?.custom_instructions ?? ""} onChange={(e) => set("custom_instructions", e.target.value)} rows={2} placeholder="Tono extra, marcas a evitar, productos a destacar..." className="resize-none" />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Contacto emergencia (nombre)</Label>
          <Input className="h-8" value={v?.emergency_contact_name ?? ""} onChange={(e) => set("emergency_contact_name", e.target.value)} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Teléfono</Label>
          <Input className="h-8" value={v?.emergency_contact_phone ?? ""} onChange={(e) => set("emergency_contact_phone", e.target.value)} />
        </div>
      </div>
      <label className="flex items-center gap-2 text-xs cursor-pointer">
        <Checkbox checked={v?.requires_publish_approval ?? true} onCheckedChange={(c) => set("requires_publish_approval", c === true)} />
        Requerir aprobación humana antes de publicar
      </label>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Horas preferidas (0-23, coma)</Label>
          <Input className="h-8" defaultValue={hours.join(", ")} onBlur={(e) => set("preferred_publishing_hours", e.target.value.split(",").map((s) => Number(s.trim())).filter((n) => !isNaN(n) && n >= 0 && n <= 23))} placeholder="9, 12, 18" key={hours.join("|")} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Zona horaria</Label>
          <Input className="h-8" value={v?.timezone ?? "America/Puerto_Rico"} onChange={(e) => set("timezone", e.target.value)} />
        </div>
      </div>
    </div>
  );
}
