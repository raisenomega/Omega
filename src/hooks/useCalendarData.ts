import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiGet, apiPatch } from "@/lib/api-client";

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

export function useCalendarList(month: string, status: CalendarStatus) {
  return useQuery<{ items: CalendarPost[]; total: number }>({
    queryKey: ["calendar_list", month, status],
    queryFn: async () => {
      const params = new URLSearchParams({ month, status });
      return apiGet<{ items: CalendarPost[]; total: number }>(`/calendar/?${params}`);
    },
    retry: 1,
  });
}

export function useUpdatePostStatus() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: DbStatus }) =>
      apiPatch(`/calendar/${id}/status`, { status }),
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
