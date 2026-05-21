import type { UseFormReturn } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionSamples({ form }: Props) {
  const { toast } = useToast();
  const samples = form.watch("brand_voice_samples") ?? [];
  const text = samples.join("\n\n");

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground bg-muted/40 px-3 py-2 rounded">
        Pega 3-5 ejemplos · o sube PDF · ARIA también aprenderá de tus aprobaciones.
      </p>
      <div className="space-y-1">
        <Label className="text-xs">Ejemplos (línea en blanco separa)</Label>
        <Textarea
          rows={3}
          value={text}
          onChange={(e) => form.setValue(
            "brand_voice_samples",
            e.target.value.split(/\n\s*\n/).map((s) => s.trim()).filter(Boolean),
          )}
          placeholder="Pega aquí tus mejores posts, uno por párrafo..."
          className="resize-none"
        />
        <p className="text-xs text-muted-foreground">{samples.length} muestra(s) detectada(s)</p>
      </div>
      <div className="space-y-1">
        <Label className="text-xs">PDF info del negocio (opcional)</Label>
        <Input
          type="file"
          accept="application/pdf"
          className="h-8"
          onChange={() => toast({ title: "PDF parsing próximamente", description: "DEBT-039 · Fase 3 · pypdf + Claude Haiku" })}
        />
      </div>
    </div>
  );
}
