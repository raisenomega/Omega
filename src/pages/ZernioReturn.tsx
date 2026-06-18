import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

/** B-2 headless · aterrizaje del retorno OAuth de Zernio (corre DENTRO del popup). SOLO relay:
 * avisa al opener vía postMessage para que refresque el estado REAL desde connected-accounts, y cierra.
 * NO afirma conexión por sí mismo — el verde lo decide connected-accounts en el opener (honestidad P1). */
export default function ZernioReturn() {
  const [params] = useSearchParams();
  const status = params.get("zernio") ?? "";
  const platform = params.get("platform") ?? "";
  useEffect(() => {
    try {
      window.opener?.postMessage(
        { source: "zernio", status, platform }, window.location.origin);
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
