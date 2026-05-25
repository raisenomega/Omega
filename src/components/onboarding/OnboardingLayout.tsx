import type { UseFormReturn } from "react-hook-form";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SECTIONS } from "./sections/registry";

interface OnboardingLayoutProps {
  form: UseFormReturn<OnboardingForm>;
  activeIndex: number;
  clientId?: string | null;  // DEBT-039 V2 · pasado a Component (SectionSamples lo usa)
  onPendingFile?: (f: File | null) => void;  // FIX 1 · SectionBusiness retiene doc para subir al crear
}

// Renderiza Section[activeIndex] · banner opcional inline al lado del título
// (definido en registry · ver SectionDef.banner).
export function OnboardingLayout({ form, activeIndex, clientId, onPendingFile }: OnboardingLayoutProps) {
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
        <Comp form={form} clientId={clientId} onPendingFile={onPendingFile} />
      </div>
    </div>
  );
}
