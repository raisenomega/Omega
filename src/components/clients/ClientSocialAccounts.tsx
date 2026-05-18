import { useState } from "react";
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

const PLATFORMS = [
  { value: "instagram", label: "Instagram", emoji: "📸" },
  { value: "facebook", label: "Facebook", emoji: "📘" },
  { value: "tiktok", label: "TikTok", emoji: "🎵" },
  { value: "twitter", label: "X / Twitter", emoji: "🐦" },
  { value: "linkedin", label: "LinkedIn", emoji: "💼" },
  { value: "youtube", label: "YouTube", emoji: "🎬" },
];

interface ClientSocialAccountsProps {
  clientId: string;
  organizationId: string;
}

export function ClientSocialAccounts({ clientId, organizationId }: ClientSocialAccountsProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [platform, setPlatform] = useState("instagram");
  const [accountName, setAccountName] = useState("");
  const [accountUrl, setAccountUrl] = useState("");
  const [followersCount, setFollowersCount] = useState("");

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

  const createMutation = useMutation({
    mutationFn: async () => {
      const { error } = await supabase.from("social_accounts").insert({
        client_id: clientId,
        organization_id: organizationId,
        platform,
        account_name: accountName,
        account_url: accountUrl || null,
        followers_count: followersCount ? parseInt(followersCount) : 0,
        connected: true,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["social_accounts", clientId] });
      queryClient.invalidateQueries({ queryKey: ["social_accounts"] });
      setDialogOpen(false);
      setAccountName("");
      setAccountUrl("");
      setFollowersCount("");
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
    PLATFORMS.find((pl) => pl.value === p) || { label: p, emoji: "🌐" };

  return (
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
                    {PLATFORMS.map((p) => (
                      <SelectItem key={p.value} value={p.value}>
                        {p.emoji} {p.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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
              <div className="space-y-2">
                <Label>URL del perfil</Label>
                <Input
                  value={accountUrl}
                  onChange={(e) => setAccountUrl(e.target.value)}
                  placeholder="https://instagram.com/usuario"
                />
              </div>
              <div className="space-y-2">
                <Label>Seguidores</Label>
                <Input
                  type="number"
                  value={followersCount}
                  onChange={(e) => setFollowersCount(e.target.value)}
                  placeholder="0"
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
              const config = platformConfig(acc.platform);
              return (
                <div
                  key={acc.id}
                  className="flex items-center gap-3 rounded-lg border border-border/30 bg-muted/20 p-2.5"
                >
                  <span className="text-lg">{config.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{acc.account_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(acc.followers_count ?? 0).toLocaleString()} seguidores
                    </p>
                  </div>
                  {acc.connected && <div className="h-2 w-2 rounded-full bg-success" />}
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
      </CardContent>
    </Card>
  );
}
