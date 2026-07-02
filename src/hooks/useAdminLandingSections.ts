// Admin de landing_sections (Sitio Web · owner-only). Lectura + escritura por Supabase client
// directo (excepción válida, igual que useLandingSections/useSuperOwner) · la RLS super_owner de
// landing_sections protege el UPDATE. En esta rebanada solo mutamos is_visible y display_order.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface AdminSection {
  id: string;
  name: string;
  is_visible: boolean;
  display_order: number;
}

const KEY = ["admin_landing_sections"];

export function useAdminLandingSections() {
  const qc = useQueryClient();

  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("landing_sections")
        .select("id, name, is_visible, display_order")
        .order("display_order");
      if (error) throw error;
      return (data ?? []) as AdminSection[];
    },
  });

  const patch = useMutation({
    mutationFn: async ({ id, ...fields }: { id: string } & Partial<Omit<AdminSection, "id">>) => {
      const { error } = await supabase.from("landing_sections").update(fields).eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });

  return { sections: query.data ?? [], isLoading: query.isLoading, patch };
}
