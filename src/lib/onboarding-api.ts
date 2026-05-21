// API client onboarding · centraliza fetch + auth header.
import { supabase } from "@/integrations/supabase/client";
import type { OnboardingForm } from "./onboarding-schema";

interface OnboardingResponse {
  client_id: string;
  completion_percent: number;
  onboarding_complete: boolean;
}

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${session?.access_token ?? ""}`,
  };
}

function apiBase(): string {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const e = await res.json().catch(() => ({}));
    throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchOnboardingData(clientId: string): Promise<OnboardingForm> {
  const res = await fetch(`${apiBase()}/clients/${clientId}/onboarding-data`, {
    headers: await authHeaders(),
  });
  return handleResponse<OnboardingForm>(res);
}

export async function postOnboarding(data: OnboardingForm): Promise<OnboardingResponse> {
  const res = await fetch(`${apiBase()}/clients/onboarding`, {
    method: "POST",
    headers: await authHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<OnboardingResponse>(res);
}

export async function patchOnboarding(clientId: string, data: OnboardingForm): Promise<OnboardingResponse> {
  const res = await fetch(`${apiBase()}/clients/${clientId}/onboarding-data`, {
    method: "PATCH",
    headers: await authHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<OnboardingResponse>(res);
}
