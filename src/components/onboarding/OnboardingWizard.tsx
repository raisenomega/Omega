import { useEffect, useMemo, useState } from "react";
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

  return (
    <div className="flex h-full flex-col">
      <WizardHeader completionPercent={wizard.completionPercent} onClose={onClose} />

      <HorizontalStepper
        activeIndex={activeIndex}
        completedIndices={completedIndices}
        onJump={setActiveIndex}
      />

      <OnboardingLayout form={wizard.form} activeIndex={activeIndex} />

      <WizardFooter
        activeIndex={activeIndex}
        totalSections={SECTIONS.length}
        isLast={isLast}
        canSubmit={canSubmit}
        isSubmitting={wizard.isSubmitting}
        onPrev={() => setActiveIndex((i) => Math.max(0, i - 1))}
        onNext={() => setActiveIndex((i) => Math.min(SECTIONS.length - 1, i + 1))}
        onSubmit={wizard.submit}
      />
    </div>
  );
}
