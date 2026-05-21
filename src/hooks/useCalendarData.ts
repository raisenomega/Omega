import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "./use-toast";

export type CalendarStatus = "all" | "scheduled" | "published" | "failed" | "cancelled";
export type DbStatus = "pending" | "publishing" | "published" | "failed" | "cancelled";

export interface CalendarPost {
  id: string;
  client_id: string;
  platform: string | null;
  content_preview: string;
  scheduled_for: string;
  status: DbStatus;
  platform_post_id: string | null;
  error_message: string | null;
}

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` };
}

const apiBase = () => import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export function useCalendarList(month: string, status: CalendarStatus) {
  return useQuery<{ items: CalendarPost[]; total: number }>({
    queryKey: ["calendar_list", month, status],
    queryFn: async () => {
      const params = new URLSearchParams({ month, status });
      const res = await fetch(`${apiBase()}/calendar/?${params}`, { headers: await authHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    retry: 1,
  });
}

export function useUpdatePostStatus() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: DbStatus }) => {
      const res = await fetch(`${apiBase()}/calendar/${id}/status`, {
        method: "PATCH", headers: await authHeaders(), body: JSON.stringify({ status }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${res.status}`); }
      return res.json();
    },
    onSuccess: (_r, vars) => {
      qc.invalidateQueries({ queryKey: ["calendar_list"] });
      toast({ title: vars.status === "cancelled" ? "Cancelado" : "Reactivado" });
    },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });
}

export function dateKey(iso: string): string {
  return iso.slice(0, 10);
}

export function groupByDay(posts: CalendarPost[]): Map<string, CalendarPost[]> {
  const map = new Map<string, CalendarPost[]>();
  for (const p of posts) {
    const k = dateKey(p.scheduled_for);
    const arr = map.get(k) ?? [];
    arr.push(p);
    map.set(k, arr);
  }
  return map;
}

export function getPostsForDay(grouped: Map<string, CalendarPost[]>, day: string): CalendarPost[] {
  return grouped.get(day) ?? [];
}
