// Detecta is_super_owner (operador OMEGA · Ibrain). Lectura simple de auth →
// Supabase directo (excepción válida, igual que useProAccess). Filtra por
// is_super_owner=true (owner_user_id no es único · el flag vive en 1 sola fila).
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export function useSuperOwner(): { isSuperOwner: boolean; loading: boolean } {
  const { user } = useAuth();
  const q = useQuery({
    queryKey: ["super-owner", user?.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("resellers")
        .select("id")
        .eq("owner_user_id", user!.id)
        .eq("is_super_owner", true)
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return !!data;
    },
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000,
  });
  return { isSuperOwner: q.data ?? false, loading: !!user?.id && q.isLoading };
}
