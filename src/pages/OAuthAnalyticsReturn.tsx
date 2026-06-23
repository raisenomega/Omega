import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

/** Retorno OAuth de analítica (Google/Meta · corre DENTRO del popup). SOLO relay: avisa al opener por
 * BroadcastChannel SAME-ORIGIN para que refresque el estado REAL desde /oauth/{provider}/status, y cierra.
 * NO afirma conexión (P1 · el verde lo decide el status en el opener, no este redirect). Calco de
 * ZernioReturn (probado en prod) · canal "oauth-analytics" · fallback storage si no hay BroadcastChannel. */
export default function OAuthAnalyticsReturn() {
  const [params] = useSearchParams();
  const provider = params.get("provider") ?? "";
  const status = params.get("status") ?? "";
  useEffect(() => {
    const payload = { source: "oauth-analytics", provider, status };
    try {
      if (typeof BroadcastChannel !== "undefined") {
        const ch = new BroadcastChannel("oauth-analytics");
        ch.postMessage(payload);
        ch.close();
      } else {
        localStorage.setItem("oauth-analytics", JSON.stringify({ ...payload, t: Date.now() }));  // dispara storage event
        localStorage.removeItem("oauth-analytics");
      }
    } finally {
      window.close();   // si el navegador bloquea el close, queda el mensaje de abajo
    }
  }, [provider, status]);
  return (
    <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
      Conexión procesada. Podés cerrar esta ventana.
    </div>
  );
}
