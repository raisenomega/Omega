// @vitest-environment jsdom
// A2.2 · UX downgrade: una cuenta en enterprise perpetuo (cuenta-dueño · sin sub Stripe) NO debe
// ver el CTA "Bajar a …" (pegaría 409 no_active_subscription). Se oculta el downgrade cuando el
// plan actual es enterprise. Un usuario real en PRO sí puede bajar a básico (sigue visible).
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/hooks/useUpgradePlan", () => ({
  useUpgradePlan: () => ({ mutate: vi.fn(), isPending: false }),
}));

import { PlanCard } from "@/components/addons/PlanCard";

const noop = () => {};

describe("PlanCard · downgrade oculto en enterprise (A2.2)", () => {
  it("enterprise actual → NO muestra 'Bajar a' en planes inferiores", () => {
    render(<PlanCard planCode="basic" currentPlan="enterprise" clientId="c1" onRequestDowngrade={noop} />);
    expect(screen.queryByText(/Bajar a/i)).toBeNull();
  });

  it("PRO actual → SÍ muestra 'Bajar a' en básico (usuario real con sub Stripe)", () => {
    render(<PlanCard planCode="basic" currentPlan="pro" clientId="c1" onRequestDowngrade={noop} />);
    expect(screen.getByText(/Bajar a/i)).toBeTruthy();
  });
});
