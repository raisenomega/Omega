import { Check } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import type { LandingTier } from "@/hooks/useLandingPricing";
import type { LandingLang } from "@/landing/i18n/landing-strings";

// Réplica visual del PricingTierCard del molde: badge "Recomendado", nombre, tagline, precio grande
// dorado + USD, features con Check dorado. El botón "Comprar" del molde (que abría el checkout) va
// NEUTRALIZADO a CTA de registro → /auth (frontera del arco: cero carrito/Stripe). Dorado = #EEA62B.
interface Props {
  tier: LandingTier;
  lang: LandingLang;
  recommendedLabel: string;
  cta: string;
}

export function PricingTierCard({ tier, lang, recommendedLabel, cta }: Props) {
  const name = lang === "es" ? tier.name_es : tier.name_en;
  const tagline = lang === "es" ? tier.tagline_es : tier.tagline_en;
  const features = (lang === "es" ? tier.features_es : tier.features_en).filter(Boolean);

  return (
    <div
      className={`relative flex flex-col rounded-xl border p-6 transition-all duration-300 ${
        tier.is_recommended ? "border-primary/40 bg-card shadow-lg shadow-primary/10" : "border-border bg-card hover:border-primary/20"
      }`}
    >
      {tier.is_recommended && (
        <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground">
          {recommendedLabel}
        </Badge>
      )}
      <h3 className="mt-2 font-display text-xl font-bold text-foreground">{name}</h3>
      <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{tagline}</p>
      <p className="mt-4 font-display text-foreground">
        <span className="text-3xl font-bold text-primary">${tier.price.toLocaleString()}</span>
        <span className="ml-1 text-sm font-normal text-muted-foreground">USD</span>
      </p>
      <ul className="mt-6 flex-1 space-y-3">
        {features.map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm text-foreground">
            <Check size={16} className="mt-0.5 shrink-0 text-primary" />
            {feature}
          </li>
        ))}
      </ul>
      <Link
        to="/auth"
        className="mt-6 w-full rounded-lg bg-primary py-3 text-center text-sm font-semibold text-primary-foreground transition-transform hover:scale-[1.02]"
      >
        {cta}
      </Link>
    </div>
  );
}
