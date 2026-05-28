// ¿El usuario actual es dueño de algún reseller? (operador de cartera, no cliente
// con plan). Lectura simple de auth → Supabase directo (misma convención que
// useSuperOwner). RLS permite leer la propia fila (auth.uid() = owner_user_id).
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export function useIsReseller(): { isReseller: boolean; loading: boolean } {
  const { user } = useAuth();
  const q = useQuery({
    queryKey: ["is-reseller", user?.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("resellers")
        .select("id")
        .eq("owner_user_id", user!.id)
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return !!data;
    },
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000,
  });
  return { isReseller: q.data ?? false, loading: !!user?.id && q.isLoading };
}
