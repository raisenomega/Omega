import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useOnboardingForm } from "@/hooks/useOnboardingForm";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { StepperLayout } from "./StepperLayout";
import { SinglePageLayout } from "./SinglePageLayout";

interface OnboardingWizardProps {
  onComplete?: (clientId: string) => void;
}

function completionColor(pct: number): string {
  if (pct >= 80) return "text-emerald-600";
  if (pct >= 40) return "text-amber-600";
  return "text-rose-600";
}

export function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const wizard = useOnboardingForm(onComplete);
  useTrackOnMount("feature_open", { feature: "onboarding_wizard" });

  const identity = wizard.form.watch("identity");
  const canSubmit = !!(identity?.name && identity?.industry && identity?.region) && !wizard.isSubmitting;
  const Layout = isDesktop ? SinglePageLayout : StepperLayout;

  return (
    <div className="flex h-full max-h-[90vh] flex-col">
      <div className="border-b border-border bg-background/95 px-4 py-3 backdrop-blur sticky top-0 z-10">
        <div className="flex items-center justify-between gap-3 mb-2">
          <h2 className="text-lg font-semibold">Nuevo Cliente</h2>
          <span className={`text-sm font-medium tabular-nums ${completionColor(wizard.completionPercent)}`}>
            {wizard.completionPercent}%
          </span>
        </div>
        <Progress value={wizard.completionPercent} className="h-1.5" />
        <p className="text-xs text-muted-foreground mt-1">
          Has completado {wizard.completionPercent}% · Recomendamos 80% para que ARIA opere mejor desde el primer día
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        <Layout form={wizard.form} />
      </div>

      <div className="border-t border-border bg-background px-4 py-3 sticky bottom-0">
        <Button
          onClick={wizard.submit}
          disabled={!canSubmit}
          className="w-full"
          title={canSubmit ? "" : "Completa nombre, industria y región"}
        >
          {wizard.isSubmitting ? "Creando…" : "Crear Cliente"}
        </Button>
      </div>
    </div>
  );
}
