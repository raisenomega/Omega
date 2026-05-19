import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export interface MyPlanStatus {
  loading: boolean;
  isClient: boolean;
  isOwner: boolean;
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
        .select("id")
        .eq("owner_user_id", user!.id)
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
    enabled: !!user,
  });

  return {
    loading: !user || clientQuery.isLoading || resellerQuery.isLoading,
    isClient: !!clientQuery.data,
    isOwner: !!resellerQuery.data,
    clientId: clientQuery.data?.id ?? null,
  };
}
