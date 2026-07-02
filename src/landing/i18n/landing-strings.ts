// Fase 3 · i18n MÍNIMO scoped a la landing pública (NO globaliza OMEGA · app español-only).
// El copy del Hero vive acá (decisión owner: en código/i18n, NO en DB). ES default.
export type LandingLang = "es" | "en";

export interface LandingStrings {
  hero: { title: string; subtitle: string; cta: string };
  header: { cta: string };
  footer: { rights: string }; // fallback · el texto real sale de landing_footer_config
}

export const LANDING_STRINGS: Record<LandingLang, LandingStrings> = {
  es: {
    hero: {
      title: "Tu marketing digital, en 30 segundos",
      subtitle:
        "Deja de saltar entre Meta, Google y cinco apps más. OMEGA lee todo y te dice qué publicar esta semana — en un lenguaje que entiendes.",
      cta: "Empieza gratis 7 días",
    },
    header: { cta: "Empieza gratis" },
    footer: { rights: "Una plataforma de Raisen Agency. Todos los derechos reservados." },
  },
  en: {
    hero: {
      title: "Your digital marketing, in 30 seconds",
      subtitle:
        "Stop juggling Meta, Google and five other apps. OMEGA reads everything and tells you what to post this week — in plain language.",
      cta: "Start free for 7 days",
    },
    header: { cta: "Start free" },
    footer: { rights: "A Raisen Agency platform. All rights reserved." },
  },
};
