import { useEffect } from "react";
import { apiPost } from "@/lib/api-client";

// Behavioral tracking · fire-and-forget · NO bloquea UI
// 19 event_types canónicos (spec ARIA_NOVA_INTELLIGENCE §4.3)
// session_id: UUID generado en mount · persiste en sessionStorage
// DEBT-CL-021 cerrada: apiPost (fuente única) · catch silencia errores
// (incluye 401 si no hay JWT · OK para telemetría · cero impacto UI)

const SESSION_KEY = "aria_session_id";

function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return "";
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export async function trackEvent(
  event_type: string,
  event_data?: Record<string, unknown>,
): Promise<void> {
  try {
    await apiPost(`/aria/track`, {
      event_type,
      event_data: event_data ?? null,
      session_id: getOrCreateSessionId(),
    });
  } catch {
    /* fire-and-forget: silently swallow · no UI block */
  }
}

export function useTrackOnMount(event_type: string, event_data?: Record<string, unknown>) {
  useEffect(() => {
    void trackEvent(event_type, event_data);
  }, [event_type]);
}
