import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGoogleStatus, useGoogleConnect } from "@/hooks/useGoogleOAuth";
import { AnalyticsConnectButton } from "@/components/clients/AnalyticsConnectButton";

interface Props { clientId: string; }

/** Sección "Analítica" del tab Cuentas (debajo de las redes · /clients/{id}). Conecta Google
 * (analítica web · GA4 + Search Console) per-negocio (clientId de la RUTA). Los DATOS se ven en el
 * Centro de Inteligencia. Popup + BroadcastChannel: al volver del popup (/oauth/return) refetchea el
 * status REAL (el verde NO lo da el mensaje · P1). White-label: cero "Zernio" visible. */
export function ClientAnalyticsConnect({ clientId }: Props) {
  const gStatus = useGoogleStatus(clientId);
  const gConnect = useGoogleConnect(clientId);
  const gRefetch = gStatus.refetch;

  useEffect(() => {
    // Al volver del popup → refetch del status REAL (NO asumir conectado por el mensaje · P1).
    const refetch = () => { void gRefetch(); };
    let ch: BroadcastChannel | null = null;
    const onStorage = (e: StorageEvent) => { if (e.key === "oauth-analytics" && e.newValue) refetch(); };
    if (typeof BroadcastChannel !== "undefined") {
      ch = new BroadcastChannel("oauth-analytics");
      ch.onmessage = (e) => { if (e.data?.source === "oauth-analytics") refetch(); };
    } else {
      window.addEventListener("storage", onStorage);
    }
    return () => { ch?.close(); window.removeEventListener("storage", onStorage); };
  }, [gRefetch]);

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Analítica</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        <p className="text-xs text-muted-foreground leading-relaxed">
          Conectá Google para ver tu analítica web (GA4 + Search Console) en el Centro de Inteligencia.
        </p>
        <AnalyticsConnectButton
          label="Google" sublabel="Analítica web · sesiones, clics y búsquedas (GA4 + Search Console)"
          connected={!!gStatus.data?.connected} isPending={gConnect.isPending}
          onConnect={() => gConnect.mutate()} />
        <p className="border-t border-border/30 pt-2 text-[11px] leading-relaxed text-muted-foreground/80">
          Una vez conectada, los números y gráficas aparecen en el Centro de Inteligencia, actualizándose solos.
        </p>
      </CardContent>
    </Card>
  );
}
