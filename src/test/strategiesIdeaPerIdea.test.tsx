// @vitest-environment jsdom
// REDISEÑO ESTRATEGIAS · FASE 0 · "la idea es la unidad": el modal agrupa por red (encabezado)
// PERO cada idea tiene su PROPIA flecha (no una por red que manda todas juntas). La flecha manda
// SOLO esa idea + mark_used:FALSE → NO consume la estrategia (sigue en Activas con sus demas ideas).
// Solo frontend · revierte la decision del Commit 2 (la flecha ya no flipa a used).
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const recordUseSpy = vi.fn();
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: recordUseSpy }) }));

import { StrategyIdeaBoxes } from "@/components/strategies/StrategyIdeaBoxes";

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// IG con 3 ideas (1.1/1.2/1.3) + TikTok con 1 → el caso que rompia: usar 1.2 mandaba las 3 de IG.
const POSTS = [
  { plataforma: "Instagram", idea: "idea-ig-1" },
  { plataforma: "Instagram", idea: "idea-ig-2" },
  { plataforma: "Instagram", idea: "idea-ig-3" },
  { plataforma: "TikTok", idea: "idea-tt-1" },
];
const flechas = () => screen.getAllByRole("button", { name: /usar en content lab/i });

describe("Estrategias Fase 0 · modal por-idea + flecha no consume", () => {
  it("test_modal_idea_individual · cada idea tiene su propia flecha (no una por red)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    expect(flechas()).toHaveLength(4);   // 4 ideas → 4 flechas (NO 2, una por red)
  });

  it("test_flecha_manda_una_idea · flecha de la 1.2 → brief = SOLO esa idea (no el join de las 3)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    fireEvent.click(screen.getByRole("button", { name: /idea-ig-2/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "idea-ig-2", platform: "instagram" } });
  });

  it("test_flecha_no_consume · flecha → /use con mark_used:FALSE (la estrategia NO va a used)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    fireEvent.click(screen.getByRole("button", { name: /idea-ig-2/i }));
    expect(recordUseSpy).toHaveBeenCalledWith({ id: "s1", platform: "instagram", brief: "idea-ig-2", mark_used: false });
  });

  it("test_agrupacion_visual · las ideas siguen agrupadas bajo su red (un solo encabezado por red)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    expect(screen.getAllByText("Instagram")).toHaveLength(1);   // 1 encabezado IG con sus 3 ideas dentro
    expect(screen.getByText("TikTok")).toBeTruthy();
  });

  it("test_navega_igual · la navegacion ocurre aunque /use lance (best-effort)", () => {
    recordUseSpy.mockImplementationOnce(() => { throw new Error("use failed"); });
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    fireEvent.click(screen.getByRole("button", { name: /idea-tt-1/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "idea-tt-1", platform: "tiktok" } });
  });
});
