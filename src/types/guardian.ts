// GUARDIAN · tipos del panel (4B-4/4B-5). Alineados al schema 00022 + 00065.

export interface GuardianEvent {
  id: string;
  user_id: string | null;
  event_type: string;
  ip_address: string | null;
  user_agent: string | null;
  country: string | null;
  geo: Record<string, unknown> | null;
  session_id: string | null;
  risk_score: number;
  created_at: string;
}

export interface GuardianIncident {
  id: string;
  user_id: string | null;
  incident_type: string;
  severity: string;
  status: string;
  summary: string | null;
  evidence?: Record<string, unknown> | null;
  detected_at: string;
  resolved_at: string | null;
  resolved_by: string | null;
  resolution_notes: string | null;
}

export interface GuardianWatchEntry {
  id: string;
  ip_address: string;
  list_type: string;
  reason: string | null;
  scope_client_id: string | null;
  created_by: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface GuardianUserDetail {
  user_id: string;
  email: string | null;
  account_created: string | null;
  last_sign_in: string | null;
  last_login: GuardianEvent | null;
  history: GuardianEvent[];
  open_incidents: GuardianIncident[];
  watchlist_matches: GuardianWatchEntry[];
}

// Apertura del modal universal (Sub-B) desde cualquier card.
export interface OpenGuardianDetail {
  kind: "event" | "incident" | "watchlist";
  userId?: string | null;
  ip?: string;
  incidentId?: string;
}

// Claude Consultor (Sub-E).
export interface ConsultResponse {
  analysis: string;
  recommended_action: string;
  confidence_level: string;
  reasoning: string;
  alternative?: string | null;
}
