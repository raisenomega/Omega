import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";
import { useClientPlanStatus } from "@/hooks/useClientPlanStatus";
import { useUpgradePlan } from "@/hooks/useUpgradePlan";

interface PlanSectionProps { clientId: string | null; }

export function PlanSection({ clientId }: PlanSectionProps) {
  const status = useClientPlanStatus(clientId ?? "");
  const upgrade = useUpgradePlan();

  if (!clientId) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-base">Plan</CardTitle></CardHeader>
        <CardContent className="text-sm text-muted-foreground">Sin cliente asociado. Contacta a tu reseller.</CardContent>
      </Card>
    );
  }

  const cta = (() => {
    if (status.planCode === "pro" || status.planCode === "enterprise") {
      return <Badge variant="secondary" className="gap-1"><Check className="h-3 w-3" />Plan PRO activo</Badge>;
    }
    if (status.planCode === "basic") {
      return <Button onClick={() => upgrade.mutate({ clientId, targetPlan: "pro" })} disabled={upgrade.isPending} className="w-full">{upgrade.isPending ? "Procesando…" : "Subir a PRO $65/mes"}</Button>;
    }
    return <Button onClick={() => upgrade.mutate({ clientId, targetPlan: "basic" })} disabled={upgrade.isPending} className="w-full">{upgrade.isPending ? "Procesando…" : "Activar BÁSICO $29/mes"}</Button>;
  })();

  return (
    <Card>
      <CardHeader><CardTitle className="text-base flex items-center justify-between">Plan<span className="text-xs font-normal text-muted-foreground uppercase tabular-nums">{status.planConfig.label}</span></CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="text-sm text-muted-foreground">
          {status.loading ? "Cargando…" : (
            <>
              <div>Precio: <span className="text-foreground font-medium">{status.planConfig.priceLabel}</span></div>
              <div>Posts del ciclo: <span className="text-foreground tabular-nums">{status.postsUsed} / {status.postsTotal || "—"}</span></div>
              {status.renewsInDays !== null && <div>Renueva en {status.renewsInDays} días</div>}
            </>
          )}
        </div>
        <div className="space-y-1">
          {status.features.unlocked.slice(0, 4).map((f) => (
            <div key={f.key} className="text-xs text-muted-foreground flex items-center gap-1"><Check className="h-3 w-3 text-emerald-500" />{f.label}</div>
          ))}
        </div>
        {cta}
      </CardContent>
    </Card>
  );
}
