import { useCallback, useMemo, useState } from "react";
import { useOnboardingForm } from "@/hooks/useOnboardingForm";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { sectionsFilled } from "@/lib/onboarding-completion";
import { SECTIONS } from "./sections/registry";
import { WizardHeader } from "./WizardHeader";
import { HorizontalStepper } from "./HorizontalStepper";
import { OnboardingLayout } from "./OnboardingLayout";
import { WizardFooter } from "./WizardFooter";

interface OnboardingWizardProps {
  onComplete?: (clientId: string) => void;
  onClose?: () => void;
}

export function OnboardingWizard({ onComplete, onClose }: OnboardingWizardProps) {
  const wizard = useOnboardingForm(onComplete);
  const [activeIndex, setActiveIndex] = useState(0);
  useTrackOnMount("feature_open", { feature: "onboarding_wizard" });

  const values = wizard.form.watch();
  const filled = useMemo(() => sectionsFilled(values), [values]);
  const completedIndices = useMemo(
    () => new Set(filled.map((f, i) => (f ? i : -1)).filter((i) => i >= 0)),
    [filled],
  );
  const identityValid = filled[0];

  const canJumpTo = useCallback(
    (target: number) => target <= activeIndex || identityValid,
    [activeIndex, identityValid],
  );

  const isLast = activeIndex === SECTIONS.length - 1;
  const canSubmit = identityValid && !wizard.isSubmitting;

  return (
    <div className="flex h-full flex-col">
      <WizardHeader completionPercent={wizard.completionPercent} onClose={onClose} />

      <HorizontalStepper
        activeIndex={activeIndex}
        completedIndices={completedIndices}
        onJump={setActiveIndex}
        canJumpTo={canJumpTo}
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
