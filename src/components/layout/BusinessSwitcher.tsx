import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";

// Cosmético puro (Sprint 7 close · NAVEGACION_SPRINT7_CIERRE.md): muestra el negocio
// activo. Cliente → nombre con punto verde. Owner (clientId null) → "Superadmin".
// Solo lectura: NO crea estado de cliente activo, NO recablea páginas, NO useActiveClient.
export function BusinessSwitcher() {
  const { clientId, loading } = useMyPlanStatus();
  const { data: name } = useQuery({
    queryKey: ["my_business_name", clientId],
    queryFn: async () => {
      const { data } = await supabase.from("clients").select("name").eq("id", clientId!).maybeSingle();
      return data?.name ?? null;
    },
    enabled: !!clientId,
  });
  if (loading) return null;
  return (
    <div className="flex items-center gap-2 rounded-md border border-sidebar-border/50 bg-sidebar-accent/30 px-2 py-1.5 text-xs group-data-[collapsible=icon]:hidden">
      {clientId ? (
        <>
          <span className="h-2 w-2 shrink-0 rounded-full bg-green-500" />
          <span className="truncate font-medium">{name ?? "Mi negocio"}</span>
        </>
      ) : (
        <span className="font-semibold text-amber-500">Superadmin</span>
      )}
    </div>
  );
}
