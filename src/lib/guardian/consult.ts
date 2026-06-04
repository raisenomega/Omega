// GUARDIAN · wrapper del endpoint Consultor (Sub-E). Mapea el kind del modal → entity_type del backend.
import { apiPost } from "@/lib/api-client";
import type { ConsultResponse, OpenGuardianDetail } from "@/types/guardian";

export function consultEntity(detail: OpenGuardianDetail, ownerQuestion?: string) {
  const entity_type = detail.kind === "incident" ? "incident" : detail.kind === "watchlist" ? "watchlist" : "user";
  const entity_id = detail.incidentId ?? (detail.kind === "watchlist" ? detail.ip : detail.userId) ?? "";
  return apiPost<ConsultResponse>("/guardian/consult/incident", { entity_type, entity_id, owner_question: ownerQuestion });
}
