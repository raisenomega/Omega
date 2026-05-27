import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { FEATURES } from "@/lib/plan-limits";

// Features comprables como add-on (tienen addonPrice). El add-on usa el feature key
// como addon_code (convención). DEBT-076: si el cliente tiene uno activo, NO lo pierde
// al bajar de plan.
const ADDON_FEATURE_KEYS = new Set(FEATURES.filter((f) => f.addonPrice).map((f) => f.key));

// Narrowing seguro desde unknown (addons puede ser null/[] o forma inesperada · cero any).
function parseActiveAddonCodes(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return raw.flatMap((item) => {
    if (typeof item !== "object" || item === null) return [];
    const rec = item as Record<string, unknown>;
    if (typeof rec.addon_code !== "string") return [];
    const deactivated = typeof rec.deactivated_at === "string" ? rec.deactivated_at : null;
    return deactivated ? [] : [rec.addon_code];
  });
}

/**
 * Set de feature keys que el cliente RETIENE vía add-on activo (client_plans.addons).
 * Hoy típicamente vacío (Crisis Room ComingSoon · sin add-on vendido aún) pero el
 * cruce queda correcto y listo: evita marcar como "pérdida" lo que se conserva.
 */
export function useClientAddonFeatureKeys(clientId: string): Set<string> {
  const { data } = useQuery({
    queryKey: ["client_addon_features", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("client_plans")
        .select("addons")
        .eq("client_id", clientId)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
    enabled: !!clientId,
  });

  return new Set(
    parseActiveAddonCodes(data?.addons).filter((code) => ADDON_FEATURE_KEYS.has(code)),
  );
}
