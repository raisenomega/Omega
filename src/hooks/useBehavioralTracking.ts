import { supabase } from "@/integrations/supabase/client";
import { useEffect } from "react";

// Behavioral tracking · fire-and-forget · NO bloquea UI
// 19 event_types canónicos (spec ARIA_NOVA_INTELLIGENCE §4.3)
// session_id: UUID generado en mount · persiste en sessionStorage

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
    const { data: { session } } = await supabase.auth.getSession();
    if (!session?.access_token) return;
    const apiBase = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
    await fetch(`${apiBase}/aria/track`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({
        event_type,
        event_data: event_data ?? null,
        session_id: getOrCreateSessionId(),
      }),
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
