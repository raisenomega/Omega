import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export function useOrganization() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const profileQuery = useQuery({
    queryKey: ["profile", user?.id],
    enabled: !!user,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("user_id", user!.id)
        .single();
      if (error) throw error;
      return data;
    },
  });

  const orgQuery = useQuery({
    queryKey: ["organization", profileQuery.data?.organization_id],
    enabled: !!profileQuery.data?.organization_id,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("organizations")
        .select("*")
        .eq("id", profileQuery.data!.organization_id!)
        .single();
      if (error) throw error;
      return data;
    },
  });

  const teamQuery = useQuery({
    queryKey: ["team", profileQuery.data?.organization_id],
    enabled: !!profileQuery.data?.organization_id,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("organization_id", profileQuery.data!.organization_id!);
      if (error) throw error;
      return data;
    },
  });

  const rolesQuery = useQuery({
    queryKey: ["user_roles", profileQuery.data?.organization_id],
    enabled: !!teamQuery.data,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("user_roles")
        .select("*");
      if (error) throw error;
      return data;
    },
  });

  const auditQuery = useQuery({
    queryKey: ["audit_logs", profileQuery.data?.organization_id],
    enabled: !!profileQuery.data?.organization_id,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("audit_logs" as any)
        .select("*")
        .order("created_at", { ascending: false })
        .limit(50);
      if (error) throw error;
      return data as any[];
    },
  });

  const updateOrg = useMutation({
    mutationFn: async (updates: { name?: string; logo_url?: string }) => {
      const { error } = await supabase
        .from("organizations")
        .update(updates)
        .eq("id", profileQuery.data!.organization_id!);
      if (error) throw error;
      // Log audit
      await supabase.from("audit_logs" as any).insert({
        organization_id: profileQuery.data!.organization_id!,
        user_id: user!.id,
        action: "update",
        entity_type: "organization",
        entity_id: profileQuery.data!.organization_id!,
        details: updates,
      } as any);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organization"] });
      queryClient.invalidateQueries({ queryKey: ["audit_logs"] });
    },
  });

  const updateRole = useMutation({
    mutationFn: async ({ userId, role }: { userId: string; role: string }) => {
      const { error } = await supabase
        .from("user_roles")
        .update({ role: role as any })
        .eq("user_id", userId);
      if (error) throw error;
      await supabase.from("audit_logs" as any).insert({
        organization_id: profileQuery.data!.organization_id!,
        user_id: user!.id,
        action: "update_role",
        entity_type: "user_role",
        entity_id: userId,
        details: { new_role: role },
      } as any);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user_roles"] });
      queryClient.invalidateQueries({ queryKey: ["audit_logs"] });
    },
  });

  const team = (teamQuery.data ?? []).map((profile) => {
    const role = rolesQuery.data?.find((r) => r.user_id === profile.user_id);
    return { ...profile, role: role?.role ?? "viewer" };
  });

  return {
    loading: profileQuery.isLoading || orgQuery.isLoading,
    profile: profileQuery.data,
    organization: orgQuery.data,
    team,
    auditLogs: auditQuery.data ?? [],
    updateOrg,
    updateRole,
    isAdmin: rolesQuery.data?.some((r) => r.user_id === user?.id && r.role === "admin") ?? false,
  };
}
