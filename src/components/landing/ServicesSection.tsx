import { useLandingLang } from "@/landing/i18n/LandingLangContext";
import { useLandingServices } from "@/hooks/useLandingServices";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { ServiceCard } from "./ServiceCard";

// Sección Servicios de la landing · réplica del molde (grid de 3, divisor+glow dorado, reveal on
// scroll). Encabezado desde i18n (réplica estricta en código). Datos reales de landing_services
// (solo is_visible · orden display_order). `section-padding` del molde → padding explícito.
export function ServicesSection() {
  const { lang, t } = useLandingLang();
  const { services } = useLandingServices();
  const { ref, isVisible } = useScrollReveal();

  return (
    <section id="services" ref={ref} className="relative overflow-hidden px-6 py-24 md:py-32">
      <div className="absolute left-1/2 top-0 -translate-x-1/2 h-px w-2/3 bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full bg-primary/[0.03] blur-[150px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-6xl">
        <div
          className={`mb-16 text-center transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"}`}
        >
          <h2 className="mb-4 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl lg:text-5xl">
            {t.services.title}
          </h2>
          <p className="mx-auto max-w-lg text-muted-foreground">{t.services.subtitle}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {services.map((service, index) => (
            <ServiceCard key={service.id} service={service} lang={lang} index={index} isVisible={isVisible} />
          ))}
        </div>
      </div>
    </section>
  );
}
