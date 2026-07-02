// Fase 3 · i18n MÍNIMO scoped a la landing pública (NO globaliza OMEGA · app español-only).
// El copy del Hero vive acá (decisión owner: en código/i18n, NO en DB). ES default.
export type LandingLang = "es" | "en";

export interface LandingStrings {
  hero: { title: string; subtitle: string; cta: string };
  services: { title: string; subtitle: string }; // encabezado de la sección (los servicios salen de DB)
  process: { title: string; subtitle: string }; // encabezado de la sección (los pasos salen de DB)
  pricing: {
    title: string; subtitle: string; // encabezado de tiers
    addonsTitle: string; addonsSubtitle: string; // encabezado de add-ons
    recommended: string; cta: string; // badge + CTA neutralizado
  };
  leadForm: { title: string; subtitle: string; pyme: string; reseller: string; name: string; email: string; phone: string; message: string; cta: string; sending: string; success: string; error: string; consent: string };
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
    services: {
      title: "Todo lo que OMEGA hace por ti",
      subtitle: "Una sola plataforma para crear, publicar y medir. Sin saltar entre apps.",
    },
    process: {
      title: "Cómo funciona OMEGA",
      subtitle: "De registrarte a publicar, en cuatro pasos.",
    },
    pricing: {
      title: "Un plan para cada etapa",
      subtitle: "Empieza gratis. Crece cuando lo necesites. Cancela cuando quieras.",
      addonsTitle: "Suma más potencia",
      addonsSubtitle: "Packs de video con IA para cuando quieras producir más.",
      recommended: "Recomendado",
      cta: "Empieza gratis",
    },
    leadForm: {
      title: "Hablemos de tu negocio",
      subtitle: "Déjanos tus datos y te contactamos.",
      pyme: "Para mi negocio", reseller: "Quiero ser agencia",
      name: "Nombre", email: "Email", phone: "Teléfono (opcional)", message: "¿En qué te ayudamos?",
      cta: "Enviar", sending: "Enviando…", success: "¡Gracias! Te contactaremos pronto.",
      error: "No pudimos enviar tu mensaje. Intenta de nuevo.",
      consent: "Al enviar aceptas que te contactemos sobre tu solicitud.",
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
    services: {
      title: "Everything OMEGA does for you",
      subtitle: "One platform to create, publish and measure. No more app-juggling.",
    },
    process: {
      title: "How OMEGA works",
      subtitle: "From sign-up to publishing, in four steps.",
    },
    pricing: {
      title: "A plan for every stage",
      subtitle: "Start free. Grow when you need to. Cancel anytime.",
      addonsTitle: "Add more power",
      addonsSubtitle: "AI video packs for when you want to produce more.",
      recommended: "Recommended",
      cta: "Start free",
    },
    leadForm: {
      title: "Let's talk about your business",
      subtitle: "Leave us your details and we'll reach out.",
      pyme: "For my business", reseller: "I want an agency",
      name: "Name", email: "Email", phone: "Phone (optional)", message: "How can we help?",
      cta: "Send", sending: "Sending…", success: "Thanks! We'll be in touch soon.",
      error: "We couldn't send your message. Please try again.",
      consent: "By submitting you agree to be contacted about your request.",
    },
    header: { cta: "Start free" },
    footer: { rights: "A Raisen Agency platform. All rights reserved." },
  },
};
