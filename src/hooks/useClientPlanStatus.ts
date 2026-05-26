import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useDemoMode } from "./useDemoMode";
import {
  getPlanConfig,
  getUnlockedFeatures,
  getLockedFeatures,
  NETWORKS,
  type PlanCode,
  type Network,
  type PlanFeature,
} from "@/lib/plan-limits";

export interface PlanStatusData {
  loading: boolean;
  planCode: PlanCode;
  planConfig: ReturnType<typeof getPlanConfig>;
  postsUsed: number;
  postsTotal: number;
  percentUsed: number;
  accountsByNetwork: Record<Network, { exists: boolean; active: boolean }>;
  features: { unlocked: PlanFeature[]; locked: PlanFeature[] };
  renewsInDays: number | null;
  renewsOn: string | null;
  hasPlan: boolean;
}

export function useClientPlanStatus(clientId: string): PlanStatusData {
  const demo = useDemoMode();  // override SOLO si email === cliente@omega.com (cero impacto real)
  const planQuery = useQuery({
    queryKey: ["client_plans", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("client_plans")
        .select("plan, current_period_start, current_period_end")
        .eq("client_id", clientId)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
    enabled: !!clientId,
  });

  const postsQuery = useQuery({
    queryKey: ["content_lab_generated", "cycle", clientId, planQuery.data?.current_period_start],
    queryFn: async () => {
      const { count, error } = await supabase
        .from("content_lab_generated")
        .select("*", { count: "exact", head: true })
        .eq("client_id", clientId)
        .neq("status", "rejected")
        .gte("created_at", planQuery.data!.current_period_start)
        .lt("created_at", planQuery.data!.current_period_end);
      if (error) throw error;
      return count ?? 0;
    },
    enabled: !!planQuery.data,
  });

  const accountsQuery = useQuery({
    queryKey: ["social_accounts", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("social_accounts")
        .select("platform, status")
        .eq("client_id", clientId);
      if (error) throw error;
      return data;
    },
    enabled: !!clientId,
  });

  const hasPlan = !!planQuery.data;
  // Default a 'adopcion' (entry tier · spec §3) cuando no hay row en client_plans:
  // cliente pre-activación ve la bar con valores zero del trial de 7 días.
  const realPlanCode = (planQuery.data?.plan ?? "adopcion") as PlanCode;
  // Demo Mode: cliente@omega.com puede simular el plan ('pro'/'basic') · resto = plan real DB.
  const planCode: PlanCode = demo.isDemoAccount ? demo.demoMode : realPlanCode;
  const planConfig = getPlanConfig(planCode);
  const postsUsed = postsQuery.data ?? 0;
  const postsTotal = planConfig.postsPerCycle === Infinity ? 0 : planConfig.postsPerCycle;
  const percentUsed = postsTotal > 0 ? Math.min(100, Math.round((postsUsed / postsTotal) * 100)) : 0;

  const accountsByNetwork = NETWORKS.reduce((acc, network) => {
    const matches = (accountsQuery.data ?? []).filter((a) => a.platform === network);
    acc[network] = { exists: matches.length > 0, active: matches.some((a) => a.status === "active") };
    return acc;
  }, {} as Record<Network, { exists: boolean; active: boolean }>);

  const features = {
    unlocked: getUnlockedFeatures(planCode),
    locked: getLockedFeatures(planCode),
  };

  const renewsInDays = planQuery.data?.current_period_end
    ? Math.max(0, Math.ceil((new Date(planQuery.data.current_period_end).getTime() - Date.now()) / 86400000))
    : null;

  return {
    loading: planQuery.isLoading || postsQuery.isLoading || accountsQuery.isLoading,
    planCode,
    planConfig,
    postsUsed,
    postsTotal,
    percentUsed,
    accountsByNetwork,
    features,
    renewsInDays,
    renewsOn: planQuery.data?.current_period_end ?? null,
    hasPlan,
  };
}
