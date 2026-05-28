// DEBT-099 · self-service onboarding · redirige al wizard si el client del user
// es el placeholder auto-creado por trigger 00006 (name='Mi negocio' · industry NULL).
// Bypass para resellers (isOwner=true) y super_owner (isSuperadmin=true).
// Pure shouldRedirectToOnboarding vive en @/lib/onboarding-redirect (testeable sin mocks).
import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";
import { useMyPlanStatus } from "./useMyPlanStatus";
import {
  ONBOARDING_PATH, shouldRedirectToOnboarding,
  type ClientPlaceholderCheck,
} from "@/lib/onboarding-redirect";

export function useAutoRedirectFirstTime(): void {
  const { user } = useAuth();
  const { isOwner, isSuperadmin, loading: planLoading } = useMyPlanStatus();
  const navigate = useNavigate();
  const location = useLocation();

  const clientQuery = useQuery({
    queryKey: ["auto_redirect_client_check", user?.id],
    queryFn: async () => {
      const { data } = await supabase
        .from("clients").select("name, industry")
        .eq("user_id", user!.id).limit(1).maybeSingle();
      return (data as ClientPlaceholderCheck | null) ?? null;
    },
    enabled: !!user && !isOwner && !isSuperadmin,
  });

  useEffect(() => {
    if (shouldRedirectToOnboarding({
      client: clientQuery.data ?? null,
      isOwner, isSuperadmin,
      loading: planLoading || clientQuery.isLoading,
      currentPath: location.pathname,
    })) {
      navigate(ONBOARDING_PATH, { replace: true });
    }
  }, [clientQuery.data, clientQuery.isLoading, isOwner, isSuperadmin, planLoading, location.pathname, navigate]);
}
