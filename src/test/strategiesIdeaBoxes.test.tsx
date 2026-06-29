// @vitest-environment jsdom
// Estrategias C3 · cuadros por red + flecha -> Content Lab. RIGUROSO: normalizacion tolerante
// (plataforma = texto libre del LLM), red rara no rompe, 1 idea no asume 3, la flecha lleva SOLO
// esa red (brief = idea de ese cuadro + platform), NO marca used, y el boton "Usar" sigue
// llevando la estrategia COMPLETA (convivencia). Cero backend.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const setStatusSpy = vi.fn();
vi.mock("@/hooks/useStrategies", () => ({ useSetStrategyStatus: () => ({ mutate: setStatusSpy, isPending: false }) }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));

import { StrategyIdeaBoxes } from "@/components/strategies/StrategyIdeaBoxes";
import { StrategyCardActions } from "@/components/strategies/StrategyCardActions";
import type { Strategy } from "@/hooks/useStrategies";

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

const arrows = () => screen.getAllByRole("button", { name: /usar la idea de/i });

describe("StrategyIdeaBoxes · cuadros por red (C3)", () => {
  it("test_ideaboxes_agrupa · IG + TikTok + Facebook -> 3 cuadros", () => {
    render(<StrategyIdeaBoxes posts={[
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
    render(<StrategyIdeaBoxes posts={[
      { plataforma: "IG", idea: "uno" },
      { plataforma: "insta", idea: "dos" },
      { plataforma: "Instagram", idea: "tres" },
    ]} />);
    expect(arrows()).toHaveLength(1);                       // todas caen en el mismo cuadro
    expect(screen.getAllByText("Instagram")).toHaveLength(1);
    expect(screen.getByText(/uno/)).toBeTruthy();
    expect(screen.getByText(/dos/)).toBeTruthy();
    expect(screen.getByText(/tres/)).toBeTruthy();          // ninguna idea se pierde
  });

  it("test_ideaboxes_red_rara · plataforma desconocida -> fallback, idea no se pierde", () => {
    render(<StrategyIdeaBoxes posts={[{ plataforma: "Reels", idea: "idea-rara" }]} />);
    expect(arrows()).toHaveLength(1);
    expect(screen.getByText(/idea-rara/)).toBeTruthy();     // la idea sigue visible
    expect(screen.getByText(/Reels/i)).toBeTruthy();        // muestra la red cruda
  });

  it("test_ideaboxes_una_idea · 1 sola idea -> 1 cuadro (no asume 3)", () => {
    render(<StrategyIdeaBoxes posts={[{ plataforma: "TikTok", idea: "sola" }]} />);
    expect(arrows()).toHaveLength(1);
  });

  it("test_flecha_navega_solo_esa_red · click IG -> brief = idea IG + platform instagram", () => {
    render(<StrategyIdeaBoxes posts={[
      { plataforma: "Instagram", idea: "idea-ig" },
      { plataforma: "TikTok", idea: "idea-tt" },
    ]} />);
    fireEvent.click(screen.getByRole("button", { name: /usar la idea de instagram/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "idea-ig", platform: "instagram" } });
    expect(navigateSpy).toHaveBeenCalledTimes(1);           // solo navega (no la estrategia completa)
  });

  it("test_flecha_no_marca_used · la flecha NO marca la estrategia como usada", () => {
    render(<StrategyIdeaBoxes posts={[{ plataforma: "Instagram", idea: "x" }]} />);
    fireEvent.click(arrows()[0]);
    expect(setStatusSpy).not.toHaveBeenCalled();            // idea suelta, no consume la estrategia
  });
});

describe("StrategyCardActions · 'Usar' sigue llevando la estrategia COMPLETA (C3 convivencia)", () => {
  const STRAT: Strategy = {
    id: "s1", client_id: "biz1", titulo: "Mi estrategia", tipo: "semanal", estado: "active",
    created_at: "2026-06-01T00:00:00Z",
    contenido: { resumen: "Resumen X", pilares: ["P1", "P2"], posts_sugeridos: [{ plataforma: "Instagram", idea: "i" }] },
  };
  it("test_usar_sigue_completo · Usar -> brief completo + marca used (cero regresion)", () => {
    render(<StrategyCardActions strategy={STRAT} />);
    fireEvent.click(screen.getByRole("button", { name: /^usar$/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "Mi estrategia · Resumen X · P1, P2" } });
    expect(setStatusSpy).toHaveBeenCalledWith({ id: "s1", estado: "used" });
  });
});
