import { Link2, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useGoogleConnect, useGoogleStatus } from "@/hooks/useGoogleOAuth";

// Botón autocontenido Conectar/Conectado a Google (Analytics + Search Console).
// Lee useGoogleStatus para el estado y dispara connect() al click. Cero emoji (lucide only).
// 503 honesto lo maneja el hook (toast) · este botón nunca finge "conectado" sin backend.
export function ConnectGoogleButton() {
  const { data: status, isLoading } = useGoogleStatus();
  const connect = useGoogleConnect();
  const connected = status?.connected === true;

  if (connected) {
    return (
      <Button variant="outline" disabled className="gap-2">
        <CheckCircle2 className="h-4 w-4" aria-hidden />
        Google conectado
      </Button>
    );
  }

  const busy = isLoading || connect.isPending;
  return (
    <Button
      variant="default"
      className="gap-2"
      disabled={busy}
      onClick={() => connect.mutate()}
    >
      {busy ? (
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
      ) : (
        <Link2 className="h-4 w-4" aria-hidden />
      )}
      Conectar Google
    </Button>
  );
}

export default ConnectGoogleButton;
