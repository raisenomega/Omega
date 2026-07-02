import { Plus } from "lucide-react";
import type { LandingAddon } from "@/hooks/useLandingPricing";
import type { LandingLang } from "@/landing/i18n/landing-strings";

// Réplica visual del PricingAddonCard del molde: caja de ícono Plus dorada, nombre, descripción,
// precio con sufijo editable (price_suffix · col 00088). Puramente informativa (sin botón · el
// carrito/checkout va aparte). Dorado = #EEA62B por el token --primary de OMEGA.
export function PricingAddonCard({ addon, lang }: { addon: LandingAddon; lang: LandingLang }) {
  const name = lang === "es" ? addon.name_es : addon.name_en;
  const description = lang === "es" ? addon.description_es : addon.description_en;

  return (
    <div className="flex flex-col rounded-xl border border-border bg-card p-6 transition-all duration-300 hover:border-primary/30">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
        <Plus size={20} className="text-primary" />
      </div>
      <h3 className="font-display text-lg font-bold text-foreground">{name}</h3>
      <p className="mt-2 flex-1 text-sm leading-relaxed text-muted-foreground">{description}</p>
      <p className="mt-4 font-display text-foreground">
        <span className="text-2xl font-bold text-primary">+${addon.price.toLocaleString()}</span>
        <span className="ml-1 text-sm font-normal text-muted-foreground">{addon.price_suffix}</span>
      </p>
    </div>
  );
}
