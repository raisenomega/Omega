import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiGet, apiPost } from "@/lib/api-client";

export type RotationUrgency = "ok" | "warn" | "urgent" | "baseline_unknown";

export interface SecretRotation {
  secret_name: string;
  last_rotated_at: string | null;
  days_since: number | null;
  max_days: number;
  urgency: RotationUrgency;
  note: string | null;
}

interface RegisterResult {
  success: boolean;
  rotation_id: string;
  secret_name: string;
  rotated_at: string;
}

export function useSecretsRotationStatus() {
  return useQuery({
    queryKey: ["secrets-rotation"],
    queryFn: () => apiGet<{ secrets: SecretRotation[] }>("/sentinel/secrets-rotation/status"),
    refetchInterval: 60 * 1000,
  });
}

export function useRegisterRotation() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: (secret_name: string): Promise<RegisterResult> =>
      apiPost<RegisterResult>("/sentinel/secrets-rotation/register", { secret_name }),
    onSuccess: (r) => {
      toast({ title: "Rotación registrada", description: `${r.secret_name} marcado como rotado hoy.` });
      qc.invalidateQueries({ queryKey: ["secrets-rotation"] });
    },
    onError: (e: unknown) =>
      toast({ variant: "destructive", title: "No se pudo registrar", description: e instanceof Error ? e.message : "Error" }),
  });
}
