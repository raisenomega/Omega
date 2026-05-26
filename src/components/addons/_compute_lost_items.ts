import { getPlanConfig, getUnlockedFeatures, type PlanCode } from "@/lib/plan-limits";

/**
 * Features/volumen que el cliente PIERDE al bajar de `currentPlan` a `targetPlan`.
 * - Features: labels desbloqueadas en current que NO están en target.
 * - Posts: si el target tiene menos posts/ciclo → línea explícita.
 * - Cuentas: si el target tiene menos cuentas/red → línea explícita.
 */
export function computeLostItems(currentPlan: PlanCode, targetPlan: PlanCode): string[] {
  const targetLabels = new Set(getUnlockedFeatures(targetPlan).map((f) => f.label));
  const lostFeatures = getUnlockedFeatures(currentPlan)
    .filter((f) => !targetLabels.has(f.label))
    .map((f) => f.label);

  const current = getPlanConfig(currentPlan);
  const target = getPlanConfig(targetPlan);
  const lost = [...lostFeatures];

  if (target.postsPerCycle < current.postsPerCycle) {
    lost.push(`Posts: ${current.postsPerCycle}/mes → ${target.postsPerCycle}/mes`);
  }
  if (target.accountsPerNetwork < current.accountsPerNetwork) {
    lost.push(`Cuentas: ${current.accountsPerNetwork}/red → ${target.accountsPerNetwork}/red`);
  }
  return lost;
}
