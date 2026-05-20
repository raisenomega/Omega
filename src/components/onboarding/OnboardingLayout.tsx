import type { UseFormReturn } from "react-hook-form";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SECTIONS } from "./sections/registry";

interface OnboardingLayoutProps {
  form: UseFormReturn<OnboardingForm>;
  activeIndex: number;
}

// Renderiza Section[activeIndex] · banner opcional inline al lado del título
// (definido en registry · ver SectionDef.banner).
export function OnboardingLayout({ form, activeIndex }: OnboardingLayoutProps) {
  const section = SECTIONS[activeIndex];
  const Comp = section.Component;
  return (
    <div className="flex-1 overflow-y-auto px-6 py-4">
      <div className="space-y-3 text-xs">
        <div className="flex items-baseline gap-2">
          <h3 className="text-base font-semibold">
            {section.title}
            {section.required && <span className="text-rose-600 ml-1">*</span>}
          </h3>
          {section.banner && (
            <span className="text-[10px] text-muted-foreground">{section.banner}</span>
          )}
        </div>
        <Comp form={form} />
      </div>
    </div>
  );
}
