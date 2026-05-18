import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

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

  const activeClients = clientsQuery.data?.filter((c) => c.active).length ?? 0;
  const totalFollowers = socialAccountsQuery.data?.reduce(
    (sum, a) => sum + (a.followers_count ?? 0),
    0
  ) ?? 0;
  const connectedAccounts = socialAccountsQuery.data?.filter((a) => a.connected).length ?? 0;
  const totalAccounts = socialAccountsQuery.data?.length ?? 0;

  // Platform breakdown
  const platforms = ["instagram", "facebook", "tiktok", "twitter", "linkedin", "youtube"];
  const platformCounts = platforms.map((p) => ({
    platform: p,
    count: socialAccountsQuery.data?.filter((a) => a.platform === p).length ?? 0,
    followers: socialAccountsQuery.data
      ?.filter((a) => a.platform === p)
      .reduce((sum, a) => sum + (a.followers_count ?? 0), 0) ?? 0,
    connected: socialAccountsQuery.data?.filter((a) => a.platform === p && a.connected).length ?? 0,
  }));

  // Recent activity (last 5 clients + accounts added)
  const recentClients = clientsQuery.data?.slice(0, 5) ?? [];
  const recentAccounts = socialAccountsQuery.data?.slice(0, 5) ?? [];

  return {
    loading: clientsQuery.isLoading || socialAccountsQuery.isLoading,
    activeClients,
    totalFollowers,
    connectedAccounts,
    totalAccounts,
    platformCounts,
    recentClients,
    recentAccounts,
    clients: clientsQuery.data ?? [],
    socialAccounts: socialAccountsQuery.data ?? [],
  };
}
