import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useAuth } from "./useAuth";

// SENTINEL 4B-5 · salud del sistema (GET /sentinel/status/ · solo superadmin)
export interface SentinelStatus {
  security_score: number;
  status: string; // presidencial | warning | critical
  last_scan: string | null;
  deploy_decision: string; // APPROVE | BLOCK
  active_issues: unknown[];
}

export function useSentinelStatus() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["sentinel_status", user?.id],
    queryFn: () => apiGet<SentinelStatus>("/sentinel/status/"),
    enabled: !!user,
    retry: false, // sentinel_scans no migrada / 403 → empty state honesto, no spam
  });
}
