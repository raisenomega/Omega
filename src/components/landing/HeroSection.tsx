import { Link } from "react-router-dom";
import { ArrowDown } from "lucide-react";
import { useLandingLang } from "@/landing/i18n/LandingLangContext";

// Hero foreground (z-10) · renderiza SIN esperar al Canvas 3D (que va detrás, z-0). Copy en prod
// (F1) vía i18n. Un solo <h1> (base SEO de F4). CTA → /auth. Dorado OMEGA #EEA62B.
export function HeroSection() {
  const { t } = useLandingLang();
  return (
    <section
      id="hero"
      className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 text-center"
    >
      <div className="relative z-10 mx-auto max-w-4xl space-y-6">
        <h1 className="animate-fade-up font-display text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl md:text-6xl">
          {t.hero.title}
        </h1>
        <p
          className="mx-auto max-w-2xl animate-fade-up text-base leading-relaxed text-white/70 sm:text-lg"
          style={{ animationDelay: "150ms" }}
        >
          {t.hero.subtitle}
        </p>
        <div className="animate-fade-up pt-2" style={{ animationDelay: "300ms" }}>
          <Link
            to="/auth"
            className="inline-flex items-center justify-center rounded-full bg-[#EEA62B] px-8 py-3.5 font-display text-base font-semibold text-black transition-transform hover:scale-105"
          >
            {t.hero.cta}
          </Link>
        </div>
      </div>

      <div
        className="absolute bottom-8 left-1/2 z-10 -translate-x-1/2 animate-fade-up"
        style={{ animationDelay: "800ms" }}
      >
        <ArrowDown size={16} className="animate-bounce text-white/40" />
      </div>
    </section>
  );
}
