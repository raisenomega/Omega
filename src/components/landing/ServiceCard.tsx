import type { LandingService } from "@/hooks/useLandingServices";
import type { LandingLang } from "@/landing/i18n/landing-strings";
import { serviceIcon } from "./service-icons";

// Réplica visual EXACTA del ServiceCard del molde: caja de ícono dorado arriba, título,
// descripción y bullets con punto dorado. Las clases `primary` del molde resuelven a #EEA62B
// (el --primary de OMEGA = hsl(38 85% 55%) = #EEA62B). Adaptado a columnas planas _es/_en.
interface ServiceCardProps {
  service: LandingService;
  lang: LandingLang;
  index: number;
  isVisible: boolean;
}

export function ServiceCard({ service, lang, index, isVisible }: ServiceCardProps) {
  const Icon = serviceIcon(service.icon);
  const title = lang === "es" ? service.title_es : service.title_en;
  const description = lang === "es" ? service.description_es : service.description_en;
  const benefits = lang === "es" ? service.benefits_es : service.benefits_en;

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border border-border bg-card p-8 transition-all duration-700 hover:border-primary/40 hover:shadow-[0_0_40px_-10px_hsl(var(--primary)/0.25)] ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
      style={{ transitionDelay: `${200 + index * 150}ms` }}
    >
      {/* Shimmer overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.03] via-transparent to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-primary/5 blur-3xl opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

      <div className="relative z-10">
        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20 transition-all duration-300 group-hover:bg-primary/15 group-hover:ring-primary/40 group-hover:shadow-[0_0_20px_-5px_hsl(var(--primary)/0.3)]">
          <Icon size={22} />
        </div>

        <h3 className="mb-3 font-display text-xl font-bold text-foreground">{title}</h3>

        <p className="mb-6 text-sm leading-relaxed text-muted-foreground">{description}</p>

        <ul className="space-y-2.5">
          {benefits.map((benefit) => (
            <li key={benefit} className="flex items-start gap-2 text-sm text-muted-foreground">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70 shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
              {benefit}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
