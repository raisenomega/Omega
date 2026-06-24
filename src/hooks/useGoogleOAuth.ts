import { useMutation, useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useToast } from "./use-toast";

// Google OAuth (Analytics + Search Console) · RONDA D. Patrón espejo de useVideoPackCheckout.
// connect() redirige al consent de Google · useGoogleStatus() refleja si el cliente ya conectó.
// 503 honesto (sin app registrada) → toast claro, sin fabricar estado conectado.

interface AuthorizeResponse {
  authorize_url: string;
}

export interface GoogleStatus {
  connected: boolean;
  scopes: string | null;
  has_refresh: boolean;
}

export function useGoogleStatus(clientId: string) {
  return useQuery<GoogleStatus, Error>({
    queryKey: ["oauth", "google", "status", clientId],
    queryFn: () => apiGet<GoogleStatus>(`/oauth/google/status?client_id=${encodeURIComponent(clientId)}`),
    enabled: !!clientId,
    staleTime: 30_000,
  });
}

export function useGoogleConnect(clientId: string) {
  const { toast } = useToast();
  return useMutation<void, Error, void>({
    mutationFn: async () => {
      const data = await apiGet<AuthorizeResponse>(`/oauth/google/authorize?client_id=${encodeURIComponent(clientId)}`);
      if (!data.authorize_url) throw new Error("Sin authorize_url en respuesta backend");
      window.open(data.authorize_url, "_blank", "noopener,noreferrer,width=600,height=720"); // popup · vuelve por /oauth/return
    },
    onError: (e: Error) => {
      const msg = e.message;
      const notConfigured = msg.includes("google_not_configured") || msg.includes("crypto_not_configured");
      toast({
        title: notConfigured ? "Google no configurado aún" : "No se pudo conectar Google",
        description: notConfigured
          ? "La integración con Google todavía no está habilitada. Avisanos."
          : msg,
        variant: "destructive",
      });
    },
  });
}
