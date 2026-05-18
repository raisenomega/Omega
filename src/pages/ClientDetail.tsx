import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Users, Globe, UserCheck, FileText, Loader2, Bot } from "lucide-react";
import { ClientSocialAccounts } from "@/components/clients/ClientSocialAccounts";
import { ClientAIConfig } from "@/components/clients/ClientAIConfig";

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: client, isLoading } = useQuery({
    queryKey: ["client", id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("clients")
        .select("*")
        .eq("id", id!)
        .single();
      if (error) throw error;
      return data;
    },
    enabled: !!id,
  });

  // Team members for agent assignment
  const { data: teamMembers } = useQuery({
    queryKey: ["team_members"],
    queryFn: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return [];
      const { data: profile } = await supabase
        .from("profiles")
        .select("organization_id")
        .eq("user_id", user.id)
        .single();
      if (!profile?.organization_id) return [];
      const { data, error } = await supabase
        .from("profiles")
        .select("user_id, full_name, avatar_url")
        .eq("organization_id", profile.organization_id);
      if (error) throw error;
      return data ?? [];
    },
  });

  // Client posts
  const { data: posts } = useQuery({
    queryKey: ["client_posts", id],
    queryFn: async () => {
      if (!client?.organization_id) return [];
      const { data, error } = await supabase
        .from("posts")
        .select("*")
        .eq("organization_id", client.organization_id)
        .order("created_at", { ascending: false })
        .limit(20);
      if (error) throw error;
      return data ?? [];
    },
    enabled: !!client?.organization_id,
  });

  const assignMutation = useMutation({
    mutationFn: async (userId: string | null) => {
      const { error } = await supabase
        .from("clients")
        .update({ assigned_to: userId } as any)
        .eq("id", id!);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client", id] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast({ title: "Agente asignado correctamente" });
    },
    onError: (e) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!client) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Cliente no encontrado</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate("/clients")}>
          Volver a Clientes
        </Button>
      </div>
    );
  }

  const assignedMember = teamMembers?.find((m) => m.user_id === (client as any).assigned_to);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/clients")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{client.name}</h1>
            <Badge variant="secondary" className="capitalize">{client.plan}</Badge>
            {client.active && <div className="h-2.5 w-2.5 rounded-full bg-success" />}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {[client.company, client.email, client.phone].filter(Boolean).join(" · ")}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="social" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 max-w-2xl">
          <TabsTrigger value="social" className="gap-1.5">
            <Globe className="h-3.5 w-3.5" />
            Cuentas
          </TabsTrigger>
          <TabsTrigger value="agent" className="gap-1.5">
            <UserCheck className="h-3.5 w-3.5" />
            Agente
          </TabsTrigger>
          <TabsTrigger value="ai" className="gap-1.5">
            <Bot className="h-3.5 w-3.5" />
            AI
          </TabsTrigger>
          <TabsTrigger value="posts" className="gap-1.5">
            <FileText className="h-3.5 w-3.5" />
            Posts
          </TabsTrigger>
          <TabsTrigger value="info" className="gap-1.5">
            <Users className="h-3.5 w-3.5" />
            Info
          </TabsTrigger>
        </TabsList>

        {/* Social Accounts Tab */}
        <TabsContent value="social">
          <ClientSocialAccounts
            clientId={client.id}
            organizationId={client.organization_id}
          />
        </TabsContent>

        {/* Agent Assignment Tab */}
        <TabsContent value="agent">
          <Card className="border-border/50 bg-card/60">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Agente Asignado</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Selecciona el miembro del equipo responsable de gestionar este cliente.
              </p>
              <Select
                value={(client as any).assigned_to ?? "none"}
                onValueChange={(v) => assignMutation.mutate(v === "none" ? null : v)}
              >
                <SelectTrigger className="w-full max-w-sm">
                  <SelectValue placeholder="Sin agente asignado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Sin agente asignado</SelectItem>
                  {teamMembers?.map((m) => (
                    <SelectItem key={m.user_id} value={m.user_id}>
                      {m.full_name || "Sin nombre"}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {assignedMember && (
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border/30 bg-muted/20">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <UserCheck className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{assignedMember.full_name || "Sin nombre"}</p>
                    <p className="text-xs text-muted-foreground">Agente responsable</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Config Tab */}
        <TabsContent value="ai">
          <ClientAIConfig clientId={client.id} organizationId={client.organization_id} />
        </TabsContent>

        {/* Posts Tab */}
        <TabsContent value="posts">
          <Card className="border-border/50 bg-card/60">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Historial de Posts</CardTitle>
            </CardHeader>
            <CardContent>
              {!posts || posts.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-8">
                  No hay posts asociados a esta organización aún.
                </p>
              ) : (
                <div className="space-y-2">
                  {posts.map((post) => (
                    <div
                      key={post.id}
                      className="flex items-center gap-3 p-3 rounded-lg border border-border/30 bg-muted/20"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{post.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs capitalize">
                            {post.platform}
                          </Badge>
                          <Badge
                            variant={post.status === "published" ? "default" : "secondary"}
                            className="text-xs capitalize"
                          >
                            {post.status}
                          </Badge>
                        </div>
                      </div>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Info Tab */}
        <TabsContent value="info">
          <Card className="border-border/50 bg-card/60">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Información del Cliente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { label: "Nombre", value: client.name },
                { label: "Email", value: client.email },
                { label: "Teléfono", value: client.phone },
                { label: "Empresa", value: client.company },
                { label: "Plan", value: client.plan },
                { label: "Notas", value: client.notes },
                { label: "Creado", value: new Date(client.created_at).toLocaleDateString() },
              ].map((item) => (
                <div key={item.label} className="flex justify-between items-start py-2 border-b border-border/20 last:border-0">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  <span className="text-sm font-medium text-right max-w-[60%]">
                    {item.value || "—"}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
