import { useState } from "react";
import type { UseFormReturn } from "react-hook-form";
import { Button } from "@/components/ui/button";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SECTIONS } from "./sections/registry";

interface StepperLayoutProps {
  form: UseFormReturn<OnboardingForm>;
}

export function StepperLayout({ form }: StepperLayoutProps) {
  const [step, setStep] = useState(0);
  const last = SECTIONS.length - 1;
  const current = SECTIONS[step];
  const Comp = current.Component;

  const canNext = step === 0 ? !!form.watch("identity.name") && !!form.watch("identity.industry") && !!form.watch("identity.region") : true;

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Sección {step + 1} de {SECTIONS.length}</span>
        <span>{current.title}</span>
      </div>
      <h3 className="text-base font-semibold">{current.title}{current.required && <span className="text-rose-600 ml-1">*</span>}</h3>
      <Comp form={form} />
      <div className="flex gap-2 pt-2">
        <Button variant="outline" disabled={step === 0} onClick={() => setStep((s) => Math.max(0, s - 1))} className="flex-1">
          Anterior
        </Button>
        {step < last && (
          <Button onClick={() => setStep((s) => Math.min(last, s + 1))} disabled={!canNext} className="flex-1">
            Siguiente
          </Button>
        )}
      </div>
    </div>
  );
}
