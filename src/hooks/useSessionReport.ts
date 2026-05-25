import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useAuth } from "./useAuth";

// GUARDIAN 4B-4 · resumen de seguridad de la cuenta (GET /guardian/session-report)
export interface SecurityEventItem {
  event_type: string;
  ip: string;
  at: string;
  risk_score: number;
}

export interface SessionReport {
  status: string;
  last_login: { at: string; ip: string } | null;
  recent_events: SecurityEventItem[];
  open_incidents: number;
  active_signals: string[];
}

export function useSessionReport() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["guardian_session_report", user?.id],
    queryFn: () => apiGet<SessionReport>("/guardian/session-report"),
    enabled: !!user,
    retry: false, // si las tablas 00022 no están migradas → 500 → empty state, no spamear
  });
}
