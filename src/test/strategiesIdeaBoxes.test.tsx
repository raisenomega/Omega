// @vitest-environment jsdom
// Estrategias · agrupacion VISUAL por red (encabezado) + 1 flecha POR IDEA (Fase 0 · la idea es la
// unidad). RIGUROSO: normalizacion tolerante (plataforma = texto libre del LLM), red rara no rompe,
// las ideas no se pierden. La flecha lleva SOLO esa idea (brief = idea + platform) con mark_used=FALSE
// (NO consume la estrategia). El boton "Usar" sigue llevando la estrategia COMPLETA. Cero backend.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const setStatusSpy = vi.fn();
vi.mock("@/hooks/useStrategies", () => ({ useSetStrategyStatus: () => ({ mutate: setStatusSpy, isPending: false }) }));
const recordUseSpy = vi.fn();
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: recordUseSpy }) }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));

import { StrategyIdeaBoxes } from "@/components/strategies/StrategyIdeaBoxes";
import { StrategyCardActions } from "@/components/strategies/StrategyCardActions";
import type { Strategy } from "@/hooks/useStrategies";

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

const arrows = () => screen.getAllByRole("button", { name: /usar en content lab/i });

describe("StrategyIdeaBoxes · agrupacion visual por red + 1 flecha por idea (Fase 0)", () => {
  it("test_ideaboxes_agrupa · IG + TikTok + Facebook -> 3 cuadros", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[
      { plataforma: "Instagram", idea: "a" },
      { plataforma: "TikTok", idea: "b" },
      { plataforma: "Facebook", idea: "c" },
    ]} />);
    expect(arrows()).toHaveLength(3);
    expect(screen.getByText("Instagram")).toBeTruthy();
    expect(screen.getByText("TikTok")).toBeTruthy();
    expect(screen.getByText("Facebook")).toBeTruthy();
  });

  it("test_ideaboxes_normaliza · IG/insta/Instagram -> un solo cuadro Instagram", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[
      { plataforma: "IG", idea: "uno" },
      { plataforma: "insta", idea: "dos" },
      { plataforma: "Instagram", idea: "tres" },
    ]} />);
    expect(screen.getAllByText("Instagram")).toHaveLength(1);   // un solo encabezado IG (agrupacion)
    expect(arrows()).toHaveLength(3);                       // pero 1 flecha por idea (3 ideas)
    expect(screen.getByText(/uno/)).toBeTruthy();
    expect(screen.getByText(/dos/)).toBeTruthy();
    expect(screen.getByText(/tres/)).toBeTruthy();          // ninguna idea se pierde
  });

  it("test_ideaboxes_red_rara · plataforma desconocida -> fallback, idea no se pierde", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[{ plataforma: "Reels", idea: "idea-rara" }]} />);
    expect(arrows()).toHaveLength(1);
    expect(screen.getByText(/idea-rara/)).toBeTruthy();     // la idea sigue visible
    expect(screen.getByText(/Reels/i)).toBeTruthy();        // muestra la red cruda
  });

  it("test_ideaboxes_una_idea · 1 sola idea -> 1 cuadro (no asume 3)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[{ plataforma: "TikTok", idea: "sola" }]} />);
    expect(arrows()).toHaveLength(1);
  });

  it("test_flecha_navega_solo_esa_idea · click idea IG -> brief = SOLO esa idea + platform instagram", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[
      { plataforma: "Instagram", idea: "idea-ig" },
      { plataforma: "TikTok", idea: "idea-tt" },
    ]} />);
    fireEvent.click(screen.getByRole("button", { name: /idea-ig/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "idea-ig", platform: "instagram" } });
    expect(navigateSpy).toHaveBeenCalledTimes(1);           // solo esa idea (no las otras)
  });

  it("test_flecha_no_consume · Fase 0: la flecha registra via /use con mark_used=FALSE (NO consume · NO /status)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={[{ plataforma: "Instagram", idea: "x" }]} />);
    fireEvent.click(arrows()[0]);
    expect(recordUseSpy).toHaveBeenCalledWith({ id: "s1", platform: "instagram", brief: "x", mark_used: false });
    expect(setStatusSpy).not.toHaveBeenCalled();            // el uso pasa por /use, no por /status
  });
});

describe("StrategyCardActions · 'Usar' sigue llevando la estrategia COMPLETA (C3 convivencia)", () => {
  const STRAT: Strategy = {
    id: "s1", client_id: "biz1", titulo: "Mi estrategia", tipo: "semanal", estado: "active",
    created_at: "2026-06-01T00:00:00Z",
    contenido: { resumen: "Resumen X", pilares: ["P1", "P2"], posts_sugeridos: [{ plataforma: "Instagram", idea: "i" }] },
  };
  it("test_usar_sigue_completo · Usar -> brief completo + registra use completa (mark_used=true · CAPA 1)", () => {
    render(<StrategyCardActions strategy={STRAT} />);
    fireEvent.click(screen.getByRole("button", { name: /^usar$/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "Mi estrategia · Resumen X · P1, P2" } });
    expect(recordUseSpy).toHaveBeenCalledWith({ id: "s1", platform: "completa", brief: "Mi estrategia · Resumen X · P1, P2", mark_used: true });
    expect(setStatusSpy).not.toHaveBeenCalled();            // CAPA 1: el uso pasa por /use, no por /status
  });
});
