// Precios de la landing (lectura pública · RLS SELECT true). Tiers y add-ons, ambos filtran
// is_visible y ordenan por display_order. Bilingüe: columnas _es/_en crudas · el componente elige
// el idioma. price_suffix (col 00088) es el "/mes" editable de los add-ons. Cero Stripe/checkout
// (frontera del arco: comprar/carrito va aparte). CRUD del owner vive en el editor (Checkpoint C).
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface LandingTier {
  id: string;
  name_es: string;
  name_en: string;
  tagline_es: string;
  tagline_en: string;
  price: number;
  features_es: string[];
  features_en: string[];
  is_recommended: boolean;
  display_order: number;
}

export interface LandingAddon {
  id: string;
  name_es: string;
  name_en: string;
  description_es: string;
  description_en: string;
  price: number;
  price_suffix: string;
  display_order: number;
}

export function useLandingPricing() {
  const tiers = useQuery({
    queryKey: ["landing_pricing_tiers"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("landing_pricing_tiers")
        .select("id, name_es, name_en, tagline_es, tagline_en, price, features_es, features_en, is_recommended, display_order")
        .eq("is_visible", true)
        .order("display_order");
      if (error) throw error;
      return (data ?? []) as LandingTier[];
    },
  });

  const addons = useQuery({
    queryKey: ["landing_pricing_addons"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("landing_pricing_addons")
        .select("id, name_es, name_en, description_es, description_en, price, price_suffix, display_order")
        .eq("is_visible", true)
        .order("display_order");
      if (error) throw error;
      return (data ?? []) as LandingAddon[];
    },
  });

  return {
    tiers: tiers.data ?? [],
    addons: addons.data ?? [],
    isLoading: tiers.isLoading || addons.isLoading,
  };
}
