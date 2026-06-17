import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api-client";
import { platformLabel, connectButtonState } from "@/lib/zernioConnect";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Link2, CheckCircle2 } from "lucide-react";

interface Props { clientId: string; platform: string; connected: boolean; onSynced: () => void; }

/** B-2 · conecta UNA red de UN negocio vía OAuth hosteado (profile-scoped). White-label: la
 * etiqueta es la red, jamás "Zernio". HONESTIDAD (P1): abrir el popup NO afirma conexión — el
 * verde '✓ [red]' sale SOLO de `connected` (verdad real del profile · GET connected-accounts).
 * Tras abrir, ofrece 'Verificar conexión' (dispara zernio-sync hardened) y SIEMPRE permite
 * reintentar 'Vincular' (no queda atrapado si cerró el login sin autorizar). */
export function ZernioConnectButton({ clientId, platform, connected, onSynced }: Props) {
  const { toast } = useToast();
  const [awaitingVerify, setAwaitingVerify] = useState(false);
  const label = platformLabel(platform);
  const state = connectButtonState(connected, awaitingVerify);

  const openOAuth = async () => {
    const r = await apiGet<{ auth_url: string }>(
      `/clients/${clientId}/social-accounts/${platform}/connect-url`);
    window.open(r.auth_url, "_blank", "noopener,noreferrer,width=600,height=720");
    setAwaitingVerify(true);   // ofrece verificar · NO afirma conexión (el verde solo viene de `connected`)
  };

  const verify = useMutation({
    mutationFn: () => apiPost(`/clients/${clientId}/social-accounts/${platform}/zernio-sync`, {}),
    onSuccess: () => { setAwaitingVerify(false); onSynced(); toast({ title: `${label} conectado` }); },
    onError: (e: Error) => toast({                       // ante error queda en 'awaiting' → puede re-Vincular o re-Verificar
      title: `No se pudo verificar ${label}`,
      description: e.message.includes("not_in_profile")
        ? "La cuenta no quedó conectada para este negocio. Reintentá la conexión."
        : e.message,
      variant: "destructive",
    }),
  });

  if (state === "connected") {
    return (
      <span className="flex items-center gap-1 text-xs text-success">
        <CheckCircle2 className="h-3.5 w-3.5" />{label}
      </span>
    );
  }

  const connectBtn = (
    <Button variant="outline" size="sm" className="h-7 text-xs animate-pulse border-amber-500/60 text-amber-600"
            onClick={() => void openOAuth()}>
      <Link2 className="mr-1 h-3 w-3" />Vincular {label}
    </Button>
  );
  if (state === "connect") return connectBtn;

  // state === "awaiting": reintentar (Vincular) + verificar · ningún texto afirma conexión.
  return (
    <div className="flex items-center gap-1">
      {connectBtn}
      <Button variant="default" size="sm" className="h-7 text-xs" disabled={verify.isPending}
              onClick={() => verify.mutate()}>
        {verify.isPending && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}Verificar conexión
      </Button>
    </div>
  );
}
