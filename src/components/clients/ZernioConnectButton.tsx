import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api-client";
import { platformLabel } from "@/lib/zernioConnect";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Link2, CheckCircle2 } from "lucide-react";

interface Props { clientId: string; platform: string; connected: boolean; onSynced: () => void; }

/** B-2 · conecta UNA red de UN negocio vía el OAuth hosteado (profile-scoped). White-label:
 * etiqueta = nombre de la red, jamás "Zernio". El estado 'connected' lo da la verdad real del
 * profile (connected-accounts), no el @handle. "Ya conecté" dispara zernio-sync (hardened). */
export function ZernioConnectButton({ clientId, platform, connected, onSynced }: Props) {
  const { toast } = useToast();
  const [opened, setOpened] = useState(false);
  const label = platformLabel(platform);

  const openOAuth = async () => {
    const r = await apiGet<{ auth_url: string }>(
      `/clients/${clientId}/social-accounts/${platform}/connect-url`);
    window.open(r.auth_url, "_blank", "noopener,noreferrer,width=600,height=720");
    setOpened(true);
  };

  const sync = useMutation({
    mutationFn: () => apiPost(`/clients/${clientId}/social-accounts/${platform}/zernio-sync`, {}),
    onSuccess: () => { setOpened(false); onSynced(); toast({ title: `${label} conectado` }); },
    onError: (e: Error) => toast({
      title: `No se pudo verificar ${label}`,
      description: e.message.includes("not_in_profile")
        ? "La cuenta no quedó conectada para este negocio. Reintentá la conexión."
        : e.message,
      variant: "destructive",
    }),
  });

  if (connected) {
    return (
      <span className="flex items-center gap-1 text-xs text-success">
        <CheckCircle2 className="h-3.5 w-3.5" />{label}
      </span>
    );
  }
  return !opened ? (
    <Button variant="outline" size="sm" className="h-7 text-xs animate-pulse border-amber-500/60 text-amber-600"
            onClick={() => void openOAuth()}>
      <Link2 className="mr-1 h-3 w-3" />Vincular {label}
    </Button>
  ) : (
    <Button variant="default" size="sm" className="h-7 text-xs" disabled={sync.isPending}
            onClick={() => sync.mutate()}>
      {sync.isPending && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}Ya conecté · verificar
    </Button>
  );
}
