import { useMutation, useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useToast } from "./use-toast";
import { useDemoMode } from "./useDemoMode";

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

const STATUS_KEY = ["oauth", "google", "status"];

export function useGoogleStatus() {
  return useQuery<GoogleStatus, Error>({
    queryKey: STATUS_KEY,
    queryFn: () => apiGet<GoogleStatus>(`/oauth/google/status`),
    staleTime: 30_000,
  });
}

export function useGoogleConnect() {
  const { toast } = useToast();
  const { isDemoAccount } = useDemoMode();
  return useMutation<void, Error, void>({
    mutationFn: async () => {
      // Demo Mode: la cuenta demo NUNCA dispara el OAuth real de Google.
      if (isDemoAccount) {
        toast({ title: "Modo demo", description: "Conectar Google no está disponible en la cuenta de demo." });
        return;
      }
      const data = await apiGet<AuthorizeResponse>(`/oauth/google/authorize`);
      if (!data.authorize_url) throw new Error("Sin authorize_url en respuesta backend");
      window.location.href = data.authorize_url; // Redirect externo al consent de Google
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
