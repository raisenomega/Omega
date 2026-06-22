import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Plus, Wifi, Trash2, Loader2 } from "lucide-react";
import { getNetworkIcon } from "@/lib/network-icons";
import { ZernioConnectButton } from "@/components/clients/ZernioConnectButton";
import { ZernioPagePicker } from "@/components/clients/ZernioPagePicker";
import { isConnected, accountFollowers, type ConnectedItem } from "@/lib/zernioConnect";
import { apiGet } from "@/lib/api-client";
import {
  CONNECTABLE_PLATFORMS,
  COMING_SOON_PLATFORMS,
  TAB_PLATFORMS_LEGEND,
} from "@/lib/social-platforms-tab";

interface ClientSocialAccountsProps {
  clientId: string;
}

export function ClientSocialAccounts({ clientId }: ClientSocialAccountsProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [platform, setPlatform] = useState("instagram");
  const [accountName, setAccountName] = useState("");
  const [pagePickerPlatform, setPagePickerPlatform] = useState<string | null>(null);  // FB select_page

  const { data: accounts, isLoading } = useQuery({
    queryKey: ["social_accounts", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("social_accounts")
        .select("*")
        .eq("client_id", clientId)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  // B-2 · estado REAL de conexión por red (del profile del negocio · alimenta el parpadeo).
  const { data: connected, refetch: refetchConnected } = useQuery({
    queryKey: ["zernio_connected", clientId],
    queryFn: () => apiGet<{ items: ConnectedItem[] }>(`/clients/${clientId}/connected-accounts`),
  });

  // B-2 headless · el popup de /zernio/return avisa al terminar el OAuth por un canal SAME-ORIGIN
  // (BroadcastChannel · funciona con noopener; window.opener.postMessage era no-op por noopener) → fallback
  // evento storage. SOLO re-consultamos la verdad real (connected-accounts); el mensaje NO afirma conexión:
  // el verde sigue saliendo de `connected.items`. (Misma honestidad que el postMessage, canal que SÍ funciona.)
  useEffect(() => {
    const handle = (d: { source?: string; status?: string; platform?: string } | null) => {
      if (d?.source !== "zernio") return;
      if (d.status === "connected") void refetchConnected();      // verde de connected-accounts, NO de este mensaje
      else if (d.status === "needs_page" && d.platform) setPagePickerPlatform(d.platform);  // FB → page-picker
    };
    let ch: BroadcastChannel | null = null;
    const onStorage = (e: StorageEvent) => {
      if (e.key !== "zernio-oauth" || !e.newValue) return;
      try { handle(JSON.parse(e.newValue)); } catch { /* noop */ }
    };
    if (typeof BroadcastChannel !== "undefined") {
      ch = new BroadcastChannel("zernio-oauth");
      ch.onmessage = (e) => handle(e.data);
    } else {
      window.addEventListener("storage", onStorage);
    }
    return () => { ch?.close(); window.removeEventListener("storage", onStorage); };
  }, [refetchConnected]);

  const createMutation = useMutation({
    mutationFn: async () => {
      // Cero sintético (P1): NO escribimos approx_followers a mano. Los seguidores reales se traen
      // de Zernio al VINCULAR (connected-accounts · followers_count) y se muestran en vivo, sin
      // persistir un número que pueda quedar stale. La cuenta nace solo con handle/plataforma.
      const { error } = await supabase.from("social_accounts").insert({
        client_id: clientId,
        platform,
        account_name: accountName,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["social_accounts", clientId] });
      queryClient.invalidateQueries({ queryKey: ["social_accounts"] });
      setDialogOpen(false);
      setAccountName("");
      toast({ title: "Cuenta social agregada" });
    },
    onError: (e) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("social_accounts").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["social_accounts", clientId] });
      queryClient.invalidateQueries({ queryKey: ["social_accounts"] });
      toast({ title: "Cuenta eliminada" });
    },
    onError: (e) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate();
  };

  const platformConfig = (p: string) =>
    CONNECTABLE_PLATFORMS.find((pl) => pl.value === p) || { label: p };

  return (
    <>
    <Card className="border-border/50 bg-card/60">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-sm font-medium">Cuentas Sociales</CardTitle>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <Plus className="mr-1 h-3 w-3" />
              Agregar
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-sm">
            <DialogHeader>
              <DialogTitle>Nueva Cuenta Social</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Plataforma</Label>
                <Select value={platform} onValueChange={setPlatform}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CONNECTABLE_PLATFORMS.map((p) => {
                      const { icon: Icon } = getNetworkIcon(p.value);
                      return (
                        <SelectItem key={p.value} value={p.value}>
                          <span className="flex items-center gap-2">
                            <Icon className="h-4 w-4" />
                            {p.label}
                          </span>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
                {/* Coming soon · DEBAJO del picker, NO dentro: informativo, gris, sin botón →
                    que nadie las confunda con conectables. Habilitar: ver DEBT-PLATFORMS-*. */}
                <p className="text-[11px] text-muted-foreground/70 pt-1">
                  Próximamente: {COMING_SOON_PLATFORMS.map((p) => p.label).join(" · ")}
                </p>
              </div>
              <div className="space-y-2">
                <Label>Nombre de cuenta *</Label>
                <Input
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                  placeholder="@usuario"
                  required
                />
              </div>
              <Button type="submit" className="w-full gradient-primary" disabled={createMutation.isPending}>
                {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Agregar Cuenta
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
          </div>
        ) : !accounts || accounts.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-4">
            Sin cuentas sociales vinculadas
          </p>
        ) : (
          <div className="space-y-2">
            {accounts.map((acc) => {
              const { icon: Icon } = getNetworkIcon(acc.platform);
              // Seguidores REALES de Zernio (connected-accounts) · null → '—', nunca 0 inventado (P1).
              const followers = accountFollowers(acc.platform, connected?.items ?? []);
              return (
                <div
                  key={acc.id}
                  className="flex items-center gap-3 rounded-lg border border-border/30 bg-muted/20 p-2.5"
                >
                  <Icon className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{acc.account_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {followers !== null ? `${followers.toLocaleString()} seguidores` : "—"}
                    </p>
                  </div>
                  {acc.status === "active" && <div className="h-2 w-2 rounded-full bg-success" />}
                  <ZernioConnectButton
                    clientId={clientId}
                    platform={acc.platform}
                    connected={isConnected(acc.platform, connected?.items ?? [])}
                    onSynced={() => { void refetchConnected(); }}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-muted-foreground hover:text-destructive"
                    onClick={() => deleteMutation.mutate(acc.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              );
            })}
          </div>
        )}
        <p className="mt-3 border-t border-border/30 pt-2 text-[11px] leading-relaxed text-muted-foreground/80">
          {TAB_PLATFORMS_LEGEND}
        </p>
      </CardContent>
    </Card>
    {pagePickerPlatform && (
      <ZernioPagePicker
        clientId={clientId}
        platform={pagePickerPlatform}
        onClose={() => setPagePickerPlatform(null)}
        onConnected={() => { void refetchConnected(); }}   // el verde lo deriva connected-accounts, no el picker
      />
    )}
    </>
  );
}
