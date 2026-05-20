import type { UseFormReturn } from "react-hook-form";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SECTIONS } from "./sections/registry";

interface OnboardingLayoutProps {
  form: UseFormReturn<OnboardingForm>;
  activeIndex: number;
}

// Renderiza la Section[activeIndex] · padding consistente · permite
// scroll INTERNO del section solo si su contenido excede el flex-1
// del wizard (caso SocialAccounts con muchas filas).
export function OnboardingLayout({ form, activeIndex }: OnboardingLayoutProps) {
  const section = SECTIONS[activeIndex];
  const Comp = section.Component;
  return (
    <div className="flex-1 overflow-y-auto px-6 py-4">
      <div className="max-w-2xl mx-auto space-y-4">
        <header className="space-y-1 pb-1">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">
            Sección {activeIndex + 1}
          </p>
          <h3 className="text-lg font-semibold">
            {section.title}
            {section.required && <span className="text-rose-600 ml-1">*</span>}
          </h3>
        </header>
        <Comp form={form} />
      </div>
    </div>
  );
}
