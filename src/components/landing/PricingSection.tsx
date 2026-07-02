import { useLandingLang } from "@/landing/i18n/LandingLangContext";
import { useLandingPricing } from "@/hooks/useLandingPricing";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { PricingTierCard } from "./PricingTierCard";
import { PricingAddonCard } from "./PricingAddonCard";

// Sección Precios de la landing · réplica del molde: grid de tiers (badge Recomendado) + grid de
// add-ons informativos. Encabezados desde i18n. Datos reales de landing_pricing_tiers/addons (solo
// is_visible · orden display_order). Grid fluido (no hardcodeado a N). Cero carrito/checkout/Stripe.
export function PricingSection() {
  const { lang, t } = useLandingLang();
  const { tiers, addons } = useLandingPricing();
  const { ref, isVisible } = useScrollReveal();

  return (
    <section id="pricing" ref={ref} className="relative overflow-hidden px-6 py-16 md:py-20">
      <div className="absolute left-1/2 top-0 -translate-x-1/2 h-px w-2/3 bg-gradient-to-r from-transparent via-primary/20 to-transparent" />

      <div
        className={`relative z-10 mx-auto max-w-6xl transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"}`}
      >
        <div className="mb-12 text-center">
          <h2 className="mb-4 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl lg:text-5xl">
            {t.pricing.title}
          </h2>
          <p className="mx-auto max-w-lg text-muted-foreground">{t.pricing.subtitle}</p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {tiers.map((tier) => (
            <PricingTierCard key={tier.id} tier={tier} lang={lang} recommendedLabel={t.pricing.recommended} cta={t.pricing.cta} />
          ))}
        </div>

        {addons.length > 0 && (
          <div className="mt-20">
            <div className="mb-12 text-center">
              <h3 className="mb-3 font-display text-2xl font-bold text-foreground md:text-3xl">{t.pricing.addonsTitle}</h3>
              <p className="mx-auto max-w-lg text-muted-foreground">{t.pricing.addonsSubtitle}</p>
            </div>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {addons.map((addon) => (
                <PricingAddonCard key={addon.id} addon={addon} lang={lang} />
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
