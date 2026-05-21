import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "./use-toast";

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

export type ContentStatus = "pending" | "saved" | "all";

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` };
}

const apiBase = () => import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export function useContentList(opts: { status: ContentStatus; contentType?: string | null }) {
  return useQuery<ContentListResult>({
    queryKey: ["content_list", opts.status, opts.contentType ?? null],
    queryFn: async () => {
      const params = new URLSearchParams({ status: opts.status, limit: "50" });
      if (opts.contentType) params.set("content_type", opts.contentType);
      const res = await fetch(`${apiBase()}/content/?${params}`, { headers: await authHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    retry: 1,
  });
}

export function useSaveContent() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: async ({ id, is_saved }: { id: string; is_saved: boolean }) => {
      const res = await fetch(`${apiBase()}/content/${id}/save`, {
        method: "PATCH", headers: await authHeaders(), body: JSON.stringify({ is_saved }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    onSuccess: (_r, vars) => {
      qc.invalidateQueries({ queryKey: ["content_list"] });
      toast({ title: vars.is_saved ? "Guardado" : "Descartado" });
    },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });
}
