import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGoogleStatus, useGoogleConnect } from "@/hooks/useGoogleOAuth";
import { useMetaStatus, useMetaOAuth } from "@/hooks/useMetaOAuth";
import { AnalyticsConnectButton } from "@/components/clients/AnalyticsConnectButton";

interface Props { clientId: string; }

/** Sección "Analítica" del tab Cuentas (debajo de las redes · /clients/{id}). Conecta Google
 * (analítica web) y Meta (métricas de redes) per-negocio (clientId de la RUTA). Los DATOS se ven en
 * el Centro de Inteligencia. Popup + BroadcastChannel: al volver del popup (/oauth/return) refetchea
 * el status REAL (el verde NO lo da el mensaje · P1). White-label: cero "Zernio" visible. */
export function ClientAnalyticsConnect({ clientId }: Props) {
  const gStatus = useGoogleStatus(clientId);
  const gConnect = useGoogleConnect(clientId);
  const mStatus = useMetaStatus(clientId);
  const { connect: mConnect } = useMetaOAuth(clientId);
  const gRefetch = gStatus.refetch, mRefetch = mStatus.refetch;

  useEffect(() => {
    // Al volver del popup → refetch del status REAL (NO asumir conectado por el mensaje · P1).
    const refetch = () => { void gRefetch(); void mRefetch(); };
    let ch: BroadcastChannel | null = null;
    const onStorage = (e: StorageEvent) => { if (e.key === "oauth-analytics" && e.newValue) refetch(); };
    if (typeof BroadcastChannel !== "undefined") {
      ch = new BroadcastChannel("oauth-analytics");
      ch.onmessage = (e) => { if (e.data?.source === "oauth-analytics") refetch(); };
    } else {
      window.addEventListener("storage", onStorage);
    }
    return () => { ch?.close(); window.removeEventListener("storage", onStorage); };
  }, [gRefetch, mRefetch]);

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Analítica</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        <p className="text-xs text-muted-foreground leading-relaxed">
          Conectá Google y Meta para ver tus métricas reales en el Centro de Inteligencia.
        </p>
        <AnalyticsConnectButton
          label="Google" sublabel="Analítica web · sesiones, clics y búsquedas (GA4 + Search Console)"
          connected={!!gStatus.data?.connected} isPending={gConnect.isPending}
          onConnect={() => gConnect.mutate()} />
        <AnalyticsConnectButton
          label="Meta" sublabel="Tus redes · seguidores, alcance e interacción de Instagram y Facebook"
          connected={!!mStatus.data?.connected} isPending={mConnect.isPending}
          onConnect={() => mConnect.mutate()} />
        <p className="border-t border-border/30 pt-2 text-[11px] leading-relaxed text-muted-foreground/80">
          Una vez conectadas, los números y gráficas aparecen en el Centro de Inteligencia, actualizándose solos.
        </p>
      </CardContent>
    </Card>
  );
}
