import { useMutation, useQuery } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { useDemoMode } from "./useDemoMode";
import { apiGet } from "@/lib/api-client";

interface AuthorizeResponse {
  authorize_url: string;
}

interface MetaStatusResponse {
  connected: boolean;
  scopes: string | null;
  external_account_id: string | null;
}

// RONDA D · OAuth Meta (Facebook/Instagram) por cliente. Patrón espejo de
// useVideoPackCheckout. Backend 503-honesto si la app de Meta no está cargada
// (META_APP_ID/SECRET) o sin OAUTH_ENCRYPTION_KEY → toast honesto, cero mock.

// Estado de la conexión Meta del cliente. Hook reservado para el arco Analytics
// (el connect de analíticas se reconstruye per-negocio ahí · DEBT-ANALYTICS-OAUTH-PER-CLIENT).
export function useMetaStatus(clientId: string) {
  return useQuery<MetaStatusResponse>({
    queryKey: ["meta-oauth-status", clientId],
    queryFn: () => apiGet<MetaStatusResponse>(`/oauth/meta/status?client_id=${encodeURIComponent(clientId)}`),
    enabled: !!clientId,
    staleTime: 30_000,
  });
}

// connect(): pide la URL del dialog OAuth y redirige el browser a Meta.
export function useMetaOAuth(clientId: string) {
  const { toast } = useToast();
  const { isDemoAccount } = useDemoMode();
  const connect = useMutation({
    mutationFn: async () => {
      // Demo Mode: la cuenta demo NUNCA dispara el OAuth real de Meta.
      if (isDemoAccount) {
        toast({ title: "Modo demo", description: "Conectar Meta no está disponible en la cuenta de demo." });
        return;
      }
      const data = await apiGet<AuthorizeResponse>(`/oauth/meta/authorize?client_id=${encodeURIComponent(clientId)}`);
      if (!data.authorize_url) throw new Error("Sin authorize_url en respuesta backend");
      window.location.href = data.authorize_url; // Redirect externo al dialog de Meta
    },
    onError: (e: Error) => {
      const msg = e.message;
      const title =
        msg.includes("meta_not_configured") ? "Meta no configurado aún"
        : msg.includes("crypto_not_configured") ? "Cifrado OAuth no configurado"
        : msg.includes("no_client_for_user") ? "Tu cuenta no tiene cliente asociado"
        : "No se pudo conectar Meta";
      const description =
        msg.includes("meta_not_configured") ? "La integración con Meta todavía no está habilitada. Avisanos."
        : msg.includes("crypto_not_configured") ? "Falta la clave de cifrado OAuth en el servidor."
        : msg;
      toast({ title, description, variant: "destructive" });
    },
  });
  return { connect };
}
