import { useEffect, useMemo, useState } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import type { UseOnboardingFormResult } from "@/hooks/useOnboardingForm";
import { sectionsFilled } from "@/lib/onboarding-completion";
import { SECTIONS } from "./sections/registry";
import { WizardHeader } from "./WizardHeader";
import { HorizontalStepper } from "./HorizontalStepper";
import { OnboardingLayout } from "./OnboardingLayout";
import { WizardFooter } from "./WizardFooter";

interface OnboardingWizardProps {
  wizard: UseOnboardingFormResult;
  onClose?: () => void;
}

export function OnboardingWizard({ wizard, onClose }: OnboardingWizardProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [visitedSections, setVisitedSections] = useState<Set<number>>(() => new Set([0]));
  useEffect(() => {
    setVisitedSections((prev) => (prev.has(activeIndex) ? prev : new Set(prev).add(activeIndex)));
  }, [activeIndex]);
  useTrackOnMount("feature_open", { feature: "onboarding_wizard" });

  const values = wizard.form.watch();
  const filled = useMemo(() => sectionsFilled(values), [values]);
  const completedIndices = useMemo(() => {
    const s = new Set<number>();
    filled.forEach((f, i) => { if (f && visitedSections.has(i)) s.add(i); });
    return s;
  }, [filled, visitedSections]);
  const identityValid = filled[0];

  const isLast = activeIndex === SECTIONS.length - 1;
  const canSubmit = identityValid && !wizard.isSubmitting;

  if (wizard.isLoading) {
    return <div className="flex h-full items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>;
  }
  if (wizard.isError) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <p className="text-sm font-medium">No se pudo cargar el cliente</p>
        {wizard.errorMessage && <p className="text-xs text-muted-foreground max-w-md">{wizard.errorMessage}</p>}
        <div className="flex gap-2 mt-2">
          <Button variant="outline" size="sm" onClick={wizard.retry}>Reintentar</Button>
          {onClose && <Button variant="ghost" size="sm" onClick={onClose}>Cerrar</Button>}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <WizardHeader completionPercent={wizard.completionPercent} isEditing={wizard.isEditing} onClose={onClose} />
      <HorizontalStepper activeIndex={activeIndex} completedIndices={completedIndices} onJump={setActiveIndex} />
      <OnboardingLayout form={wizard.form} activeIndex={activeIndex} clientId={wizard.clientId} />
      <WizardFooter
        activeIndex={activeIndex}
        totalSections={SECTIONS.length}
        isLast={isLast}
        canSubmit={canSubmit}
        isSubmitting={wizard.isSubmitting}
        isEditing={wizard.isEditing}
        onPrev={() => setActiveIndex((i) => Math.max(0, i - 1))}
        onNext={() => setActiveIndex((i) => Math.min(SECTIONS.length - 1, i + 1))}
        onSubmit={wizard.submit}
      />
    </div>
  );
}
