import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

/** B-2 headless · aterrizaje del retorno OAuth de Zernio (corre DENTRO del popup). SOLO relay: avisa al
 * opener por un canal SAME-ORIGIN para que refresque el estado REAL desde connected-accounts, y cierra.
 * NO afirma conexión — el verde lo decide connected-accounts en el opener (honestidad P1).
 * CANAL: BroadcastChannel (same-origin · funciona con noopener, a diferencia de window.opener.postMessage
 * que era un NO-OP porque window.open usa noopener) · fallback evento storage si no hay BroadcastChannel.
 * NUNCA window.opener (lo mata noopener · que se MANTIENE por anti-tabnabbing). */
export default function ZernioReturn() {
  const [params] = useSearchParams();
  const status = params.get("zernio") ?? "";
  const platform = params.get("platform") ?? "";
  useEffect(() => {
    const payload = { source: "zernio", status, platform };
    try {
      if (typeof BroadcastChannel !== "undefined") {
        const ch = new BroadcastChannel("zernio-oauth");
        ch.postMessage(payload);
        ch.close();
      } else {
        localStorage.setItem("zernio-oauth", JSON.stringify({ ...payload, t: Date.now() }));  // dispara storage event
        localStorage.removeItem("zernio-oauth");
      }
    } finally {
      window.close();   // si el navegador bloquea el close, queda el mensaje de abajo
    }
  }, [status, platform]);
  return (
    <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
      Conexión procesada. Podés cerrar esta ventana.
    </div>
  );
}
