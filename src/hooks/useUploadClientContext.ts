import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiPostFormData } from "@/lib/api-client";

interface UploadResponse {
  filename: string;
  mime: string;
  char_count: number;
  uploaded_at: string;
}

interface UploadInput {
  clientId: string;
  file: File;
}

// Sube doc contexto del cliente (PDF/DOCX/MD/TXT · cap 5MB) · backend
// extrae texto y persiste en client_context.uploaded_context_text ·
// inyectado SIEMPRE al system prompt RAFA en cada generación para ese
// cliente. Re-upload sobrescribe (V1 sin history).
export function useUploadClientContext() {
  const qc = useQueryClient();
  return useMutation<UploadResponse, Error, UploadInput>({
    mutationFn: async ({ clientId, file }) => {
      const fd = new FormData();
      fd.append("file", file);
      return apiPostFormData<UploadResponse>(`/clients/${clientId}/upload-context`, fd);
    },
    onSuccess: (_data, { clientId }) => {
      qc.invalidateQueries({ queryKey: ["client_onboarding_data", clientId] });
    },
  });
}
