// @vitest-environment jsdom
// ARCO MEDICION CAPA 1 · Commit 2 (frontend) · wire POST /strategies/{id}/use + pinta lo usado.
// CAMBIO del owner: la flecha ahora mark_used=TRUE (la estrategia VA a Usadas). El boton "Usar"
// guarda platform="completa". La tarjeta usada muestra last_used.brief + "Re-usar" (fallback al
// resumen si last_used es null · estrategias viejas). best-effort: /use NUNCA rompe la navegacion.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const recordUseMutate = vi.fn();
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: recordUseMutate }) }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));
vi.mock("@/hooks/useStrategies", () => ({ useSetStrategyStatus: () => ({ mutate: vi.fn(), isPending: false }) }));

import { StrategyIdeaBoxes } from "@/components/strategies/StrategyIdeaBoxes";
import { StrategyCardActions } from "@/components/strategies/StrategyCardActions";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import type { Strategy } from "@/hooks/useStrategies";

const STRAT = (extra: Partial<Strategy> = {}): Strategy => ({
  id: "s1", client_id: "biz1", titulo: "T-active", tipo: "semanal", estado: "active",
  created_at: "2026-06-01T00:00:00Z", contenido: { resumen: "R-generico", pilares: [], posts_sugeridos: [] }, ...extra,
});

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("CAPA 1 Commit 2 · flecha + Usar llaman /use", () => {
  it("test_flecha_llama_use · flecha IG → /use {platform:instagram, brief, mark_used:true}", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[{ plataforma: "Instagram", idea: "idea-ig" }]} />);
    fireEvent.click(screen.getByRole("button", { name: /usar la idea de instagram/i }));
    expect(recordUseMutate).toHaveBeenCalledWith({ id: "s1", platform: "instagram", brief: "idea-ig", mark_used: true });
  });

  it("test_flecha_navega_igual · la navegacion a Content Lab ocurre (best-effort)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[{ plataforma: "Instagram", idea: "idea-ig" }]} />);
    fireEvent.click(screen.getByRole("button", { name: /usar la idea de instagram/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "idea-ig", platform: "instagram" } });
  });

  it("test_flecha_use_falla_navega · si /use lanza → la navegacion IGUAL ocurre", () => {
    recordUseMutate.mockImplementationOnce(() => { throw new Error("use failed"); });
    render(<StrategyIdeaBoxes strategyId="s1" posts={[{ plataforma: "Instagram", idea: "idea-ig" }]} />);
    fireEvent.click(screen.getByRole("button", { name: /usar la idea de instagram/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "idea-ig", platform: "instagram" } });
  });

  it("test_usar_llama_use · boton 'Usar' → /use {platform:completa, brief, mark_used:true}", () => {
    render(<StrategyCardActions strategy={STRAT({ contenido: { resumen: "Resumen X", pilares: ["P1"], posts_sugeridos: [] } })} />);
    fireEvent.click(screen.getByRole("button", { name: /^usar$/i }));
    expect(recordUseMutate).toHaveBeenCalledWith({ id: "s1", platform: "completa", brief: "T-active · Resumen X · P1", mark_used: true });
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "T-active · Resumen X · P1" } });
  });
});

describe("CAPA 1 Commit 2 · la tarjeta usada pinta lo usado", () => {
  it("test_card_usada_pinta_lastused · last_used → muestra el texto usado + 'Re-usar'", () => {
    render(<StrategyCard variant="used" strategy={STRAT({ estado: "used", last_used: { platform: "instagram", brief: "texto IG usado", at: "2026-06-10T12:00:00Z" } })} />);
    expect(screen.getByText(/Usaste \(Instagram\)/i)).toBeTruthy();
    expect(screen.getByText("texto IG usado")).toBeTruthy();
    expect(screen.getByRole("button", { name: /re-?usar/i })).toBeTruthy();
  });

  it("test_card_usada_null_fallback · sin last_used (vieja) → muestra el resumen generico", () => {
    render(<StrategyCard variant="used" strategy={STRAT({ estado: "used", last_used: null })} />);
    expect(screen.getByText("R-generico")).toBeTruthy();
    expect(screen.queryByText(/Usaste \(/i)).toBeNull();
  });

  it("test_reusar · 'Re-usar' → /use + navega con el texto usado", () => {
    render(<StrategyCard variant="used" strategy={STRAT({ estado: "used", last_used: { platform: "instagram", brief: "texto IG usado", at: "x" } })} />);
    fireEvent.click(screen.getByRole("button", { name: /re-?usar/i }));
    expect(recordUseMutate).toHaveBeenCalledWith({ id: "s1", platform: "instagram", brief: "texto IG usado", mark_used: true });
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "texto IG usado", platform: "instagram" } });
  });
});
