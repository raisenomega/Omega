import type { UseFormReturn } from "react-hook-form";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SECTIONS } from "./sections/registry";

interface SinglePageLayoutProps {
  form: UseFormReturn<OnboardingForm>;
}

export function SinglePageLayout({ form }: SinglePageLayoutProps) {
  return (
    <div className="flex gap-6 p-6">
      <aside className="hidden md:block w-48 shrink-0 sticky top-0 self-start">
        <nav className="space-y-1 text-sm">
          {SECTIONS.map((s, i) => (
            <a
              key={s.id}
              href={`#section-${s.id}`}
              className="block px-2 py-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground"
            >
              {i + 1}. {s.title}
              {s.required && <span className="text-rose-600 ml-1">*</span>}
            </a>
          ))}
        </nav>
      </aside>

      <div className="flex-1 space-y-8 max-w-2xl">
        {SECTIONS.map((s) => {
          const Comp = s.Component;
          return (
            <section key={s.id} id={`section-${s.id}`} className="space-y-3 scroll-mt-24">
              <h3 className="text-lg font-semibold border-b pb-2">
                {s.title}{s.required && <span className="text-rose-600 ml-1">*</span>}
              </h3>
              <Comp form={form} />
            </section>
          );
        })}
      </div>
    </div>
  );
}
