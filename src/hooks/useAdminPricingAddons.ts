// Admin CRUD de landing_pricing_addons (Sitio Web · owner-only). Escritura por Supabase directo (RLS
// super_owner protege). SIN campos Stripe (stripe_price_id llega con el arco de checkout, aparte).
// price_suffix editable ("/mes" · col 00088).
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface AdminAddon {
  id: string;
  name_es: string;
  name_en: string;
  description_es: string;
  description_en: string;
  price: number;
  price_suffix: string;
  is_visible: boolean;
  display_order: number;
}

export type AddonDraft = Omit<AdminAddon, "id"> & { id?: string };

const KEY = ["admin_pricing_addons"];
const COLS = "id, name_es, name_en, description_es, description_en, price, price_suffix, is_visible, display_order";

export function useAdminPricingAddons() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: KEY });

  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const { data, error } = await supabase.from("landing_pricing_addons").select(COLS).order("display_order");
      if (error) throw error;
      return (data ?? []) as AdminAddon[];
    },
  });

  const save = useMutation({
    mutationFn: async (s: AddonDraft) => {
      const payload = {
        name_es: s.name_es, name_en: s.name_en, description_es: s.description_es, description_en: s.description_en,
        price: s.price, price_suffix: s.price_suffix, is_visible: s.is_visible, display_order: s.display_order,
      };
      const { error } = s.id
        ? await supabase.from("landing_pricing_addons").update(payload).eq("id", s.id)
        : await supabase.from("landing_pricing_addons").insert(payload);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("landing_pricing_addons").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const patch = useMutation({
    mutationFn: async ({ id, ...fields }: { id: string } & Partial<Omit<AdminAddon, "id">>) => {
      const { error } = await supabase.from("landing_pricing_addons").update(fields).eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  return { addons: query.data ?? [], isLoading: query.isLoading, save, remove, patch };
}
