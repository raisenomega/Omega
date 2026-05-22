import { supabase } from "@/integrations/supabase/client";
import type { Result } from "@/components/content/ResultCard";

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession();
  const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  const r = await fetch(`${base}${path}`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` }, body: JSON.stringify(body) });
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${r.status}`); }
  return r.json();
}

export const generateText = (b: { platform: string; content_type: string; topic: string; tone: string; variations: number }) => apiPost<Result>("/content-lab/generate", b);
export const generateImage = (b: { prompt: string; style: string }) => apiPost<Result>("/content-lab/generate-image", b);
export const generateVideo = (b: { prompt: string; ratio: string }) => apiPost<{ job_id: string; status: string }>("/content-lab/generate-video", b);

export interface VideoJobStatus { job_id: string; status: string; video_url?: string; error?: string }

export async function fetchVideoStatus(jobId: string): Promise<VideoJobStatus> {
  const { data: { session } } = await supabase.auth.getSession();
  const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  const r = await fetch(`${base}/content-lab/generate-video/${jobId}`, { headers: { Authorization: `Bearer ${session?.access_token ?? ""}` } });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
