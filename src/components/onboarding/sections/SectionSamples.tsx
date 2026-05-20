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
        Pega 3-5 ejemplos de tu mejor contenido reciente · O sube un PDF con info de tu negocio (opcional) · ARIA también aprenderá automáticamente de tus próximas aprobaciones.
      </p>
      <div className="space-y-1">
        <Label>Ejemplos de contenido (separa con línea en blanco)</Label>
        <Textarea
          rows={8}
          value={text}
          onChange={(e) => form.setValue(
            "brand_voice_samples",
            e.target.value.split(/\n\s*\n/).map((s) => s.trim()).filter(Boolean),
          )}
          placeholder="Post 1...\n\nPost 2...\n\nPost 3..."
        />
        <p className="text-xs text-muted-foreground">{samples.length} muestra(s) detectada(s)</p>
      </div>
      <div className="space-y-1">
        <Label>PDF con info del negocio (opcional · auto-poblar ARIA)</Label>
        <Input
          type="file"
          accept="application/pdf"
          onChange={() => toast({ title: "PDF parsing próximamente", description: "DEBT-039 · Fase 3 · pypdf + Claude Haiku" })}
        />
      </div>
    </div>
  );
}
