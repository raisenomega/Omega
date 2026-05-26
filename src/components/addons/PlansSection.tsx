import { useState } from "react";
import { Layers } from "lucide-react";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useClientPlanStatus } from "@/hooks/useClientPlanStatus";
import type { PlanCode } from "@/lib/plan-limits";
import { PAID_PLANS } from "./_plans_data";
import { PlanCard } from "./PlanCard";
import { PlanDowngradeDialog } from "./PlanDowngradeDialog";

export function PlansSection() {
  const { clientId } = useMyPlanStatus();
  const [downgradeTarget, setDowngradeTarget] = useState<PlanCode | null>(null);

  // La sección de planes solo aplica a clientes (no a owners/superadmin).
  if (!clientId) return null;

  return <PlansSectionInner clientId={clientId} downgradeTarget={downgradeTarget} setDowngradeTarget={setDowngradeTarget} />;
}

interface InnerProps {
  clientId: string;
  downgradeTarget: PlanCode | null;
  setDowngradeTarget: (t: PlanCode | null) => void;
}

function PlansSectionInner({ clientId, downgradeTarget, setDowngradeTarget }: InnerProps) {
  const status = useClientPlanStatus(clientId);

  return (
    <section id="planes" className="space-y-3">
      <div className="flex items-center gap-2">
        <Layers className="h-4 w-4 text-muted-foreground" />
        <h2 className="text-lg font-semibold">Planes</h2>
      </div>
      <p className="text-xs text-muted-foreground">Cambiá tu plan según tu volumen</p>
      <div className="grid gap-4 md:grid-cols-3">
        {PAID_PLANS.map((code) => (
          <PlanCard
            key={code}
            planCode={code}
            currentPlan={status.planCode}
            clientId={clientId}
            onRequestDowngrade={setDowngradeTarget}
          />
        ))}
      </div>
      <PlanDowngradeDialog
        open={!!downgradeTarget}
        onOpenChange={(o) => { if (!o) setDowngradeTarget(null); }}
        targetPlan={downgradeTarget ?? "basic"}
        currentPlan={status.planCode}
        renewsOn={status.renewsOn}
      />
    </section>
  );
}
