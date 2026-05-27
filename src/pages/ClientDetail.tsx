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
import { ClientAgentsActive } from "@/components/clients/ClientAgentsActive";
import { ClientAgentExecutions } from "@/components/clients/ClientAgentExecutions";
import { ClientCreditsWidget } from "@/components/clients/ClientCreditsWidget";
import { AriaUpgradeModal } from "@/components/clients/AriaUpgradeModal";
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

  // DEBT-065: Tab Agente rediseñado a nivel ARIA del cliente (sin team-member/assigned_to legacy).

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

        {/* Agent Tab · rediseño 2-col · Nivel ARIA + Créditos · fila inferior Agentes activos */}
        <TabsContent value="agent" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Columna izquierda · Nivel ARIA */}
            <Card className="border-border/50 bg-card/60">
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <UserCheck className="h-4 w-4" /> Nivel ARIA
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Badge className={ariaInfo.color}>{ariaInfo.label}</Badge>
                <p className="text-xs text-muted-foreground">{ariaInfo.desc}</p>
                <div className="flex items-center gap-2 border-t border-border/20 pt-3">
                  <span className="text-sm text-muted-foreground">Estado:</span>
                  <Badge variant={client.status === "active" ? "default" : "secondary"} className="capitalize">
                    {client.status ?? "—"}
                  </Badge>
                </div>
                <div className="pt-1">
                  <AriaUpgradeModal currentLevel={client.aria_level ?? 1} />
                </div>
              </CardContent>
            </Card>
            {/* Columna derecha · Créditos prepagados */}
            <ClientCreditsWidget clientId={client.id} />
          </div>
          {/* Fila inferior · Agentes activos (add-ons agent_*) */}
          <ClientAgentsActive clientId={client.id} />
        </TabsContent>

        {/* AI Config Tab · solo Motor de IA (Anthropic/Nano Banana/Veo) · créditos movidos al Tab Agente */}
        <TabsContent value="ai">
          <ClientAIConfig />
        </TabsContent>

        {/* Posts Tab · DEBT-053 · historial real de ejecuciones por agente */}
        <TabsContent value="posts">
          <ClientAgentExecutions clientId={client.id} />
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
