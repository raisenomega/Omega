import type { UseFormReturn } from "react-hook-form";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SECTIONS } from "./sections/registry";

interface OnboardingLayoutProps {
  form: UseFormReturn<OnboardingForm>;
  activeIndex: number;
}

// Renderiza la Section[activeIndex] · usa full width del modal full-screen.
// text-xs wrapper · reduce 1 step la tipografía global del wizard.
export function OnboardingLayout({ form, activeIndex }: OnboardingLayoutProps) {
  const section = SECTIONS[activeIndex];
  const Comp = section.Component;
  return (
    <div className="flex-1 overflow-y-auto px-6 py-4">
      <div className="space-y-3 text-xs">
        <h3 className="text-base font-semibold">
          {section.title}
          {section.required && <span className="text-rose-600 ml-1">*</span>}
        </h3>
        <Comp form={form} />
      </div>
    </div>
  );
}
