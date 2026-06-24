import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PLAN_CONFIGS, type PlanCode } from "@/lib/plan-limits";
import { useUpgradePlan } from "@/hooks/useUpgradePlan";
import { PLAN_HIGHLIGHTS, PLAN_RANK } from "./_plans_data";

interface PlanCardProps {
  planCode: "basic" | "pro" | "enterprise";
  currentPlan: PlanCode;
  clientId: string;
  onRequestDowngrade: (target: PlanCode) => void;
}

export function PlanCard({ planCode, currentPlan, clientId, onRequestDowngrade }: PlanCardProps) {
  const upgrade = useUpgradePlan();
  const config = PLAN_CONFIGS[planCode];
  const isCurrent = planCode === currentPlan;
  const isUpgrade = PLAN_RANK[planCode] > PLAN_RANK[currentPlan];
  const isDowngrade = PLAN_RANK[planCode] < PLAN_RANK[currentPlan];

  return (
    <Card
      className={`flex flex-col h-full transition-all duration-300 hover:border-amber-500/60 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)] hover:bg-gradient-to-b hover:from-amber-500/5 hover:to-transparent${isCurrent ? " border-primary" : ""}`}
    >
      <CardContent className="flex flex-col gap-3 p-4 flex-1">
        <div className="flex items-baseline justify-between gap-2">
          <h3 className="text-base font-semibold">{config.label}</h3>
          <span className="text-lg font-bold">{config.priceLabel}</span>
        </div>
        {isCurrent && <Badge variant="secondary" className="w-fit">Plan actual</Badge>}
        <ul className="space-y-1.5 flex-1">
          {PLAN_HIGHLIGHTS[planCode].map((b) => (
            <li key={b} className="flex gap-2 text-xs text-muted-foreground">
              <Check className="h-3 w-3 shrink-0 mt-0.5 text-emerald-600" />
              <span>{b}</span>
            </li>
          ))}
        </ul>

        {isCurrent ? (
          // Plan actual · no clickeable · borde gris · texto blanco (mismo patrón Add-Ons)
          <Button disabled className="w-full border border-muted-foreground/30 bg-transparent text-white disabled:opacity-100">
            Plan actual
          </Button>
        ) : isUpgrade ? (
          // Subir a X · idéntico a VideoPackCard/AgentCard (amber-border ghost → emerald hover) · ya cableado a Stripe
          <Button
            className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
            disabled={upgrade.isPending}
            onClick={() => upgrade.mutate({ clientId, targetPlan: planCode })}
          >
            {upgrade.isPending ? "Redirigiendo a Stripe…" : `Subir a ${config.label}`}
          </Button>
        ) : isDowngrade && currentPlan !== "enterprise" ? (
          // Enterprise perpetuo (cuenta-dueño · sin sub Stripe) NO ofrece downgrade (pegaría 409).
          <Button variant="secondary" className="w-full" onClick={() => onRequestDowngrade(planCode)}>
            Bajar a {config.label}
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}
