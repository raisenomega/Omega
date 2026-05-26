import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface NextScheduledPost {
  scheduled_for: string;
  content_preview: string | null;
}

// Próximo post programado del cliente: status 'pending' · scheduled_for >= ahora · CUALQUIER mes.
// Direct-Supabase (RLS scope-ea al cliente, como useDashboardData) · embed de generated_text para preview.
export function useNextScheduledPost(clientId: string | null) {
  return useQuery<NextScheduledPost | null>({
    queryKey: ["next_scheduled_post", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("scheduled_posts")
        .select("scheduled_for, content_lab_generated(generated_text)")
        .eq("status", "pending")
        .gte("scheduled_for", new Date().toISOString())
        .order("scheduled_for", { ascending: true })
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      if (!data) return null;
      const gen = (data as { content_lab_generated: { generated_text: string | null } | null })
        .content_lab_generated;
      return { scheduled_for: data.scheduled_for as string, content_preview: gen?.generated_text ?? null };
    },
    enabled: !!clientId,
  });
}
