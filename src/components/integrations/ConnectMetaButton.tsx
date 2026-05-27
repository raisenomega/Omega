import { Loader2, Link2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useMetaOAuth, useMetaStatus } from "@/hooks/useMetaOAuth";

// RONDA D · Botón self-contained para conectar Meta (Facebook/Instagram).
// Lee el estado real (useMetaStatus) y dispara el OAuth (connect). El orquestador
// lo monta donde corresponda. Cero emoji (solo iconos lucide), cero mock: si no
// hay conexión real muestra "Conectar Meta", nunca finge estar conectado.
export function ConnectMetaButton() {
  const { data: status, isLoading: statusLoading } = useMetaStatus();
  const { connect } = useMetaOAuth();
  const connected = status?.connected === true;

  if (connected) {
    return (
      <Button variant="outline" disabled className="gap-2">
        <CheckCircle2 className="text-green-600" aria-hidden />
        Meta conectado
      </Button>
    );
  }

  const busy = statusLoading || connect.isPending;
  return (
    <Button
      variant="default"
      onClick={() => connect.mutate()}
      disabled={busy}
      className="gap-2"
    >
      {busy ? <Loader2 className="animate-spin" aria-hidden /> : <Link2 aria-hidden />}
      Conectar Meta
    </Button>
  );
}
