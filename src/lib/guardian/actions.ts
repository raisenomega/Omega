// GUARDIAN · wrappers de los 4 endpoints de acción (owner-only). apiPost lanza Error con el detalle
// del backend → el caller muestra toast. Cero lógica de UI acá (solo el contrato HTTP).
import { apiPost } from "@/lib/api-client";

export interface BlockIpPayload { ip_address: string; reason: string; expires_at?: string | null; scope_client_id?: string | null; incident_id?: string | null; }
export interface ForceLogoutPayload { user_id: string; reason: string; incident_id?: string | null; }
export interface ResolveIncidentPayload { incident_id: string; resolution_notes: string; false_positive?: boolean; }
export interface PasswordResetPayload { user_id: string; reason: string; incident_id?: string | null; }

export const blockIp = (b: BlockIpPayload) => apiPost<{ ip_watchlist_id: string }>("/guardian/actions/block-ip", b);
export const forceLogout = (b: ForceLogoutPayload) => apiPost<{ method: string }>("/guardian/actions/force-logout", b);
export const resolveIncident = (b: ResolveIncidentPayload) => apiPost<{ status: string }>("/guardian/actions/resolve-incident", b);
export const triggerPasswordReset = (b: PasswordResetPayload) => apiPost<{ recovery_email_sent: boolean }>("/guardian/actions/trigger-password-reset", b);

// Presets de expiración para block-ip → ISO o null (permanente).
export function expiresFromPreset(preset: string): string | null {
  const h: Record<string, number> = { "1h": 1, "24h": 24, "7d": 168 };
  if (!(preset in h)) return null; // permanente
  return new Date(Date.now() + h[preset] * 3600 * 1000).toISOString();
}
