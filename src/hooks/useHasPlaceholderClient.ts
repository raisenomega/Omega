// DEBT-099-v2 · decide visibilidad de NudgeFirstClient.
// Placeholder = auto-trigger 00006 (name='Mi negocio' + industry NULL).
// El user lo "rompe" guardando un cliente real en /clients · el react-query
// re-evalúa en cada focus/mount → nudge desaparece automáticamente.
// Bypass owner/superadmin (no son clientes finales).
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";
import { useMyPlanStatus } from "./useMyPlanStatus";

interface ClientPlaceholderCheck { name: string; industry: string | null }

function isPlaceholderClient(c: ClientPlaceholderCheck | null): boolean {
  if (!c) return false;
  return c.name === "Mi negocio" && !c.industry;
}

export function useHasPlaceholderClient(): { isPlaceholder: boolean; loading: boolean } {
  const { user } = useAuth();
  const { isOwner, isSuperadmin, loading: planLoading } = useMyPlanStatus();

  const q = useQuery({
    queryKey: ["nudge_placeholder_check", user?.id],
    queryFn: async (): Promise<ClientPlaceholderCheck | null> => {
      const { data } = await supabase
        .from("clients").select("name, industry")
        .eq("user_id", user!.id).limit(1).maybeSingle();
      return (data as ClientPlaceholderCheck | null) ?? null;
    },
    enabled: !!user && !isOwner && !isSuperadmin,
  });

  return {
    isPlaceholder: isPlaceholderClient(q.data ?? null),
    loading: planLoading || q.isLoading,
  };
}
