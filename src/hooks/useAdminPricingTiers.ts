// Admin CRUD de landing_pricing_tiers (Sitio Web · owner-only). Escritura por Supabase directo (RLS
// super_owner protege). SIN campos Stripe (stripe_price_id llega con el arco de checkout, aparte).
// features se limpian de líneas vacías al guardar.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface AdminTier {
  id: string;
  name_es: string;
  name_en: string;
  tagline_es: string;
  tagline_en: string;
  price: number;
  features_es: string[];
  features_en: string[];
  is_recommended: boolean;
  is_visible: boolean;
  display_order: number;
}

export type TierDraft = Omit<AdminTier, "id"> & { id?: string };

const KEY = ["admin_pricing_tiers"];
const COLS =
  "id, name_es, name_en, tagline_es, tagline_en, price, features_es, features_en, is_recommended, is_visible, display_order";

export function useAdminPricingTiers() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: KEY });

  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const { data, error } = await supabase.from("landing_pricing_tiers").select(COLS).order("display_order");
      if (error) throw error;
      return (data ?? []) as AdminTier[];
    },
  });

  const save = useMutation({
    mutationFn: async (s: TierDraft) => {
      const payload = {
        name_es: s.name_es, name_en: s.name_en, tagline_es: s.tagline_es, tagline_en: s.tagline_en,
        price: s.price,
        features_es: s.features_es.map((f) => f.trim()).filter(Boolean),
        features_en: s.features_en.map((f) => f.trim()).filter(Boolean),
        is_recommended: s.is_recommended, is_visible: s.is_visible, display_order: s.display_order,
      };
      const { error } = s.id
        ? await supabase.from("landing_pricing_tiers").update(payload).eq("id", s.id)
        : await supabase.from("landing_pricing_tiers").insert(payload);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("landing_pricing_tiers").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const patch = useMutation({
    mutationFn: async ({ id, ...fields }: { id: string } & Partial<Omit<AdminTier, "id">>) => {
      const { error } = await supabase.from("landing_pricing_tiers").update(fields).eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  return { tiers: query.data ?? [], isLoading: query.isLoading, save, remove, patch };
}
