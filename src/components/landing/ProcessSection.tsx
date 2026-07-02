import { useLandingLang } from "@/landing/i18n/LandingLangContext";
import { useLandingProcess } from "@/hooks/useLandingProcess";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { ProcessStepCard } from "./ProcessStepCard";

// Sección Proceso de la landing · réplica del molde: timeline vertical (no grid), divisor+glow
// dorado, reveal on scroll con stagger por paso. El "punto de fuego" del molde (useProcessFireTracer)
// va DIFERIDO a REBANADA-PULIDO. Encabezado desde i18n. Datos reales de landing_process_steps
// (solo is_visible · orden display_order). `section-padding` del molde → padding explícito.
export function ProcessSection() {
  const { lang, t } = useLandingLang();
  const { steps } = useLandingProcess();
  const { ref, isVisible } = useScrollReveal();

  return (
    <section id="process" ref={ref} className="relative overflow-hidden px-6 py-24 md:py-32">
      <div className="absolute left-1/2 top-0 -translate-x-1/2 h-px w-2/3 bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
      <div className="absolute right-0 top-1/2 -translate-y-1/2 h-80 w-80 rounded-full bg-primary/[0.04] blur-[120px] pointer-events-none" />

      <div
        className={`relative z-10 mx-auto max-w-3xl transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"}`}
      >
        <div className="mb-16 text-center">
          <h2 className="mb-4 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl lg:text-5xl">
            {t.process.title}
          </h2>
          <p className="text-muted-foreground">{t.process.subtitle}</p>
        </div>

        <div className="mx-auto max-w-xl">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`transition-all duration-700 ${isVisible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-6"}`}
              style={{ transitionDelay: `${300 + index * 180}ms` }}
            >
              <ProcessStepCard step={step} lang={lang} isLast={index === steps.length - 1} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
