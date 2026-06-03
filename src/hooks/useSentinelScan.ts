import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";

// Botón "Correr scan ahora" · POST /sentinel/scan/ (require_superadmin · JWT auto-inyectado).
interface ScanResult {
  success: boolean;
  result?: {
    security_score: number;
    status: string;
    deploy_decision: string;
    total_issues: number;
    agents_scanned: number;
  };
}

export function useSentinelScan() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const m = useMutation({
    mutationFn: (): Promise<ScanResult> => apiPost<ScanResult>("/sentinel/scan/", { scan_type: "full" }),
    onSuccess: (r) => {
      toast({
        title: "Scan completado",
        description: `Score ${r.result?.security_score ?? "?"} · ${r.result?.agents_scanned ?? 0} componentes`,
      });
      qc.invalidateQueries({ queryKey: ["sentinel-data"] });
      qc.invalidateQueries({ queryKey: ["sentinel-history"] });
    },
    onError: (e: unknown) => {
      toast({
        variant: "destructive",
        title: "Scan falló",
        description: e instanceof Error ? e.message : "Error desconocido. Reintentá.",
      });
    },
  });
  return { runScan: () => m.mutate(), isScanning: m.isPending };
}
