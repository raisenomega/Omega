import type { LandingProcessStep } from "@/hooks/useLandingProcess";
import type { LandingLang } from "@/landing/i18n/landing-strings";
import { processIcon } from "./process-icons";

// Réplica visual del ProcessStepCard del molde: círculo de ícono + línea conectora vertical +
// número "01/02…" + título + descripción. El "encendido" que en el molde manejaba el fire-tracer
// (DIFERIDO a REBANADA-PULIDO) se preserva como hover (mismo estilo `lit` dorado del molde) y el
// contenido va SIEMPRE visible (sin el colapso por-paso que dependía del fuego). Dorado = #EEA62B.
interface Props {
  step: LandingProcessStep;
  lang: LandingLang;
  isLast: boolean;
}

export function ProcessStepCard({ step, lang, isLast }: Props) {
  const Icon = processIcon(step.icon);
  const title = lang === "es" ? step.title_es : step.title_en;
  const description = lang === "es" ? step.description_es : step.description_en;

  return (
    <div className="group relative flex gap-6">
      {!isLast && <div className="absolute left-5 top-12 h-full w-px bg-border" />}

      <div className="relative z-10 shrink-0">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-full border border-primary/20 bg-background text-primary transition-all duration-500 group-hover:border-primary group-hover:bg-primary group-hover:text-primary-foreground group-hover:shadow-[0_0_16px_4px_hsl(var(--primary)/0.4)]">
          <Icon size={18} />
        </div>
      </div>

      <div className="flex-1 pb-12">
        <p className="mb-1 font-display text-xs font-semibold uppercase tracking-[0.2em] text-primary/70">
          {String(step.step_number).padStart(2, "0")}
        </p>
        <h3 className="font-display text-lg font-bold text-foreground">{title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
