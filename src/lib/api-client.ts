import { supabase } from "@/integrations/supabase/client";

export function apiBase(): string {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
}

export async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${session?.access_token ?? ""}`,
  };
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const e = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, { headers: await authHeaders() });
  return handleResponse<T>(res);
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    method: "POST", headers: await authHeaders(), body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    method: "PATCH", headers: await authHeaders(), body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}
