import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import type { GuardianEvent, GuardianIncident, GuardianWatchEntry, GuardianUserDetail } from "@/types/guardian";

const STALE = 30 * 1000;

function qs(params: Record<string, string | boolean | undefined>): string {
  const p = Object.entries(params).filter(([, v]) => v !== undefined && v !== "");
  return p.length ? "?" + p.map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`).join("&") : "";
}

export const useGuardianEvents = (eventType?: string) =>
  useQuery({
    queryKey: ["guardian-events", eventType ?? null],
    queryFn: () => apiGet<{ events: GuardianEvent[] }>(`/guardian/events${qs({ event_type: eventType })}`),
    staleTime: STALE,
  });

export const useGuardianIncidents = (status?: string, severity?: string) =>
  useQuery({
    queryKey: ["guardian-incidents", status ?? null, severity ?? null],
    queryFn: () => apiGet<{ incidents: GuardianIncident[] }>(`/guardian/incidents${qs({ status, severity })}`),
    staleTime: STALE,
  });

export const useGuardianWatchlist = (listType?: string, activeOnly?: boolean) =>
  useQuery({
    queryKey: ["guardian-watchlist", listType ?? null, !!activeOnly],
    queryFn: () => apiGet<{ watchlist: GuardianWatchEntry[] }>(`/guardian/watchlist${qs({ list_type: listType, active_only: activeOnly })}`),
    staleTime: STALE,
  });

export const useGuardianUserDetail = (userId: string | null) =>
  useQuery({
    queryKey: ["guardian-user-detail", userId],
    queryFn: () => apiGet<GuardianUserDetail>(`/guardian/user-detail/${userId}`),
    enabled: !!userId,
    staleTime: STALE,
  });
