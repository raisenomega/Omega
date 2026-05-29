import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiGet, apiPatch } from "@/lib/api-client";

export interface ContentItem {
  id: string;
  client_id: string;
  platform: string | null;
  content_type: string;
  content: string;
  model: string | null;
  is_saved: boolean;
  created_at: string;
}

export interface ContentListResult {
  items: ContentItem[];
  total: number;
}

export type ContentStatus = "pending" | "saved" | "all" | "rejected";

export function useContentList(opts: { status: ContentStatus; contentType?: string | null }) {
  return useQuery<ContentListResult>({
    queryKey: ["content_list", opts.status, opts.contentType ?? null],
    queryFn: async () => {
      const params = new URLSearchParams({ status: opts.status, limit: "50" });
      if (opts.contentType) params.set("content_type", opts.contentType);
      return apiGet<ContentListResult>(`/content/?${params}`);
    },
    retry: 1,
  });
}

export function useSaveContent() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: ({ id, is_saved }: { id: string; is_saved: boolean }) =>
      apiPatch(`/content/${id}/save`, { is_saved }),
    onSuccess: (_r, vars) => {
      qc.invalidateQueries({ queryKey: ["content_list"] });
      toast({ title: vars.is_saved ? "Guardado" : "Descartado" });
    },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });
}

// Papelera: reusar un descartado → vuelve a borrador (mismo endpoint que save, is_saved=false).
export function useReuseContent() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: (id: string) => apiPatch(`/content/${id}/save`, { is_saved: false }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content_list"] });
      toast({ title: "Restaurado a borradores" });
    },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });
}
