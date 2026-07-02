// Envío del lead público de la landing → POST /platform/lead (endpoint FastAPI · Checkpoint A).
// apiPost lanza Error en no-2xx (429/422/500) → la mutación pasa a isError → el form muestra el
// error honesto (P1: nunca "enviado" falso). El endpoint fuerza reseller_id=NULL + source server-side.
import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";

export interface LeadPayload {
  name: string;
  email: string;
  phone?: string;
  message?: string;
  audience: "pyme" | "reseller";
  website: string; // honeypot (oculto)
}

export function useSubmitLead() {
  return useMutation({
    mutationFn: (body: LeadPayload) => apiPost<{ success: boolean }>("/platform/lead", body),
  });
}
