import { Link } from "react-router-dom";
import { useLandingLang } from "@/landing/i18n/LandingLangContext";

// Header mínimo de la landing (Rebanada 1): logo OMEGA + toggle ES/EN + CTA → /auth.
// El resto (nav, links) se difiere. Fijo arriba, backdrop-blur sobre el 3D.
export function LandingHeader() {
  const { lang, toggle, t } = useLandingLang();
  return (
    <header className="fixed left-0 right-0 top-0 z-50 flex items-center justify-between bg-background/40 px-6 py-4 backdrop-blur-sm md:px-12">
      <span className="font-display text-lg font-bold tracking-tight text-white">
        OMEGA<span className="text-[#EEA62B]">.</span>
      </span>
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          aria-label="Cambiar idioma"
          className="rounded-full border border-white/20 px-3 py-1 text-xs font-semibold text-white/70 transition-colors hover:text-white"
        >
          {lang === "es" ? "EN" : "ES"}
        </button>
        <Link
          to="/auth"
          className="rounded-full bg-[#EEA62B] px-4 py-1.5 text-xs font-semibold text-black transition-transform hover:scale-105"
        >
          {t.header.cta}
        </Link>
      </div>
    </header>
  );
}
