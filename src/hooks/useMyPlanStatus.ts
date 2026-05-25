import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export interface MyPlanStatus {
  loading: boolean;
  isClient: boolean;
  isOwner: boolean;       // dueño de cualquier reseller
  isSuperadmin: boolean;  // is_owner=true · superadmin de plataforma (00022 · §7.5)
  clientId: string | null;
}

export function useMyPlanStatus(): MyPlanStatus {
  const { user } = useAuth();

  const clientQuery = useQuery({
    queryKey: ["my_client", user?.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("clients")
        .select("id")
        .eq("user_id", user!.id)
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
    enabled: !!user,
  });

  const resellerQuery = useQuery({
    queryKey: ["my_reseller", user?.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("resellers")
        .select("*")
        .eq("owner_user_id", user!.id)
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      // is_owner (migración 00022 · superadmin) aún no en types generados → cast acotado
      return data as unknown as { id: string; is_owner: boolean } | null;
    },
    enabled: !!user,
  });

  return {
    loading: !user || clientQuery.isLoading || resellerQuery.isLoading,
    isClient: !!clientQuery.data,
    isOwner: !!resellerQuery.data,
    isSuperadmin: !!resellerQuery.data?.is_owner,
    clientId: clientQuery.data?.id ?? null,
  };
}
