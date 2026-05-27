import { getPlanConfig, getUnlockedFeatures, type PlanCode } from "@/lib/plan-limits";

/**
 * Features/volumen que el cliente PIERDE al bajar de `currentPlan` a `targetPlan`.
 * - Features: desbloqueadas en current que NO están en target NI las retiene vía add-on.
 * - Posts: si el target tiene menos posts/ciclo → línea explícita.
 * - Cuentas: si el target tiene menos cuentas/red → línea explícita.
 *
 * DEBT-076: `ownedFeatureKeys` = features que el cliente conserva por add-on activo
 * (no se listan como pérdida · ej. Crisis Room si lo compró como add-on $25).
 */
export function computeLostItems(
  currentPlan: PlanCode,
  targetPlan: PlanCode,
  ownedFeatureKeys: Set<string> = new Set(),
): string[] {
  const targetKeys = new Set(getUnlockedFeatures(targetPlan).map((f) => f.key));
  const lostFeatures = getUnlockedFeatures(currentPlan)
    .filter((f) => !targetKeys.has(f.key) && !ownedFeatureKeys.has(f.key))
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
