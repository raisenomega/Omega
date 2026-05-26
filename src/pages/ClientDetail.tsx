import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Users, Globe, UserCheck, FileText, Loader2, Bot } from "lucide-react";
import { ariaLevelInfo } from "@/lib/aria-levels";
import { ClientSocialAccounts } from "@/components/clients/ClientSocialAccounts";
import { ClientAIConfig } from "@/components/clients/ClientAIConfig";
import { fetchOnboardingData } from "@/lib/onboarding-api";
import { buildContextRows, type InfoRow } from "@/lib/client-info-fields";

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

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

  // DEBT-054: client_context (wizard) para el Info Tab · reusa el GET del onboarding · read-only.
  const { data: onboarding } = useQuery({
    queryKey: ["onboarding", id],
    queryFn: () => fetchOnboardingData(id!),
    enabled: !!id,
  });

  // DEBT-033: tabla `posts` no existe en V3 · posts retorna [] (Posts tab muestra vacío).
  // DEBT-065: Tab Agente rediseñado a nivel ARIA del cliente (sin team-member/assigned_to legacy).
  const posts: { id: string; title?: string; status?: string; created_at?: string }[] = [];

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

  const ariaInfo = ariaLevelInfo(client.aria_level);

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
            {client.status === "active" && <div className="h-2.5 w-2.5 rounded-full bg-success" />}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            {/* DEBT-066: columnas reales de clients V3 (00024) · antes leía company/email/phone inexistentes */}
            {[client.business_email, client.website, client.industry].filter(Boolean).join(" · ")}
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
          <ClientSocialAccounts clientId={client.id} />
        </TabsContent>

        {/* Agent Tab · DEBT-065 · nivel ARIA del cliente + estado (sin team-member/assigned_to legacy) */}
        <TabsContent value="agent">
          <Card className="border-border/50 bg-card/60">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <UserCheck className="h-4 w-4" /> Nivel ARIA del cliente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Badge className={ariaInfo.color}>{ariaInfo.label}</Badge>
              <p className="text-xs text-muted-foreground">{ariaInfo.desc}</p>
              <div className="flex items-center gap-2 border-t border-border/20 pt-3">
                <span className="text-sm text-muted-foreground">Estado del cliente:</span>
                <Badge variant={client.status === "active" ? "default" : "secondary"} className="capitalize">
                  {client.status ?? "—"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Config Tab · DEBT-057/058 · panel honesto Anthropic-only (read-only) */}
        <TabsContent value="ai">
          <ClientAIConfig />
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
              {([
                { label: "Nombre", value: client.name },
                { label: "Plan", value: client.plan },
                { label: "Creado", value: new Date(client.created_at).toLocaleDateString() },
                ...buildContextRows(onboarding),  // DEBT-054 · campos del wizard poblados (dinámico)
              ] as InfoRow[]).map((item) => (
                <div key={item.label} className="flex justify-between items-start py-2 border-b border-border/20 last:border-0">
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                  {item.chips ? (
                    <div className="flex flex-wrap gap-1 justify-end max-w-[60%]">
                      {item.chips.map((c) => (
                        <Badge key={c} variant="secondary" className="text-xs">{c}</Badge>
                      ))}
                    </div>
                  ) : (
                    <span className="text-sm font-medium text-right max-w-[60%] whitespace-pre-wrap">
                      {item.value || "—"}
                    </span>
                  )}
                </div>
              ))}
              {buildContextRows(onboarding).length === 0 && (
                <p className="text-xs text-muted-foreground text-center pt-2">
                  Perfil sin completar — usá "Editar" para llenar el wizard del cliente.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
