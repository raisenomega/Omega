import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

const PLATFORMS = ["instagram", "facebook", "tiktok", "twitter", "linkedin", "youtube"] as const;

function isoDaysFromNow(days: number): string {
  return new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
}

function startOfTodayIso(): string {
  const d = new Date();
  d.setHours(0, 0, 0, 0);  // medianoche local · un post pending de las 05:45 de hoy aún cuenta
  return d.toISOString();
}

export function useDashboardData() {
  const clientsQuery = useQuery({
    queryKey: ["clients"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("clients")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const socialAccountsQuery = useQuery({
    queryKey: ["social_accounts"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("social_accounts")
        .select("*, clients(name)")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const scheduledNext7dQuery = useQuery({
    queryKey: ["scheduled_posts", "next_7d"],
    queryFn: async () => {
      const { count, error } = await supabase
        .from("scheduled_posts")
        .select("*", { count: "exact", head: true })
        .in("status", ["pending", "scheduled"])  // 'scheduled' es etiqueta UI · 'pending' es DB canónico
        .gte("scheduled_for", startOfTodayIso())  // desde 00:00 de hoy · no excluye posts cuya hora ya pasó hoy
        .lte("scheduled_for", isoDaysFromNow(7));
      if (error) throw error;
      return count ?? 0;
    },
  });

  const contentLast30dQuery = useQuery({
    queryKey: ["content_lab_generated", "last_30d"],
    queryFn: async () => {
      const { count, error } = await supabase
        .from("content_lab_generated")
        .select("*", { count: "exact", head: true })
        .gte("created_at", isoDaysFromNow(-30));
      if (error) throw error;
      return count ?? 0;
    },
  });

  const activeClients = clientsQuery.data?.filter((c) => c.status === "active").length ?? 0;
  const totalClients = clientsQuery.data?.length ?? 0;
  const activeAccounts = socialAccountsQuery.data?.filter((a) => a.status === "active").length ?? 0;
  const totalAccounts = socialAccountsQuery.data?.length ?? 0;
  const scheduledNext7d = scheduledNext7dQuery.data ?? 0;
  const contentLast30d = contentLast30dQuery.data ?? 0;

  const platformCounts = PLATFORMS.map((p) => ({
    platform: p,
    count: socialAccountsQuery.data?.filter((a) => a.platform === p).length ?? 0,
    activeCount: socialAccountsQuery.data?.filter((a) => a.platform === p && a.status === "active").length ?? 0,
  }));

  const recentClients = clientsQuery.data?.slice(0, 5) ?? [];
  const recentAccounts = socialAccountsQuery.data?.slice(0, 5) ?? [];

  return {
    loading:
      clientsQuery.isLoading ||
      socialAccountsQuery.isLoading ||
      scheduledNext7dQuery.isLoading ||
      contentLast30dQuery.isLoading,
    activeClients,
    totalClients,
    activeAccounts,
    totalAccounts,
    scheduledNext7d,
    contentLast30d,
    platformCounts,
    recentClients,
    recentAccounts,
    clients: clientsQuery.data ?? [],
    socialAccounts: socialAccountsQuery.data ?? [],
  };
}
