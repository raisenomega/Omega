// @vitest-environment jsdom
// Fase B.3 · la flecha registra la idea via /use-idea con el idx CORRECTO (posicion en el array
// plano posts_sugeridos · NO el indice dentro del grupo de la red) + la tarjeta activa muestra
// "X de N ideas usadas". best-effort: el registro NO bloquea la navegacion. Solo frontend.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const recordIdeaSpy = vi.fn();
vi.mock("@/hooks/useRecordIdeaUse", () => ({ useRecordIdeaUse: () => ({ mutate: recordIdeaSpy }) }));
// StrategyCard (active) renderiza StrategyCardActions → estos hooks deben existir aunque no se usen aqui.
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: vi.fn() }) }));
vi.mock("@/hooks/useStrategies", () => ({ useSetStrategyStatus: () => ({ mutate: vi.fn(), isPending: false }) }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));

import { StrategyIdeaBoxes, buildBoxes } from "@/components/strategies/StrategyIdeaBoxes";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import type { Strategy } from "@/hooks/useStrategies";

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// IG en posiciones 0 y 2, TikTok en 1 → el idx debe ser la posicion del array plano.
const POSTS = [
  { plataforma: "Instagram", idea: "ig-0" },
  { plataforma: "TikTok", idea: "tt-1" },
  { plataforma: "Instagram", idea: "ig-2" },
];
const STRAT3: Strategy = {
  id: "s1", client_id: "biz1", titulo: "T", tipo: "semanal", estado: "active", created_at: "2026-06-01T00:00:00Z",
  contenido: { resumen: "R", pilares: [], posts_sugeridos: [{ plataforma: "ig", idea: "a" }, { plataforma: "ig", idea: "b" }, { plataforma: "tt", idea: "c" }] },
};

describe("Fase B.3 · flecha → use-idea (idx correcto) + contador X de N", () => {
  it("test_buildboxes_preserva_idx · idx = posicion en posts_sugeridos, NO dentro del grupo de la red", () => {
    const boxes = buildBoxes(POSTS);
    const ig = boxes.find((b) => b.platform === "instagram")!;
    expect(ig.ideas.map((i) => i.idx)).toEqual([0, 2]);   // ig-0 idx 0, ig-2 idx 2 (no 0 y 1)
    expect(boxes.find((b) => b.platform === "tiktok")!.ideas[0].idx).toBe(1);
  });

  it("test_flecha_llama_use_idea · flecha de ig-2 → /use-idea {idea_idx:2, platform, brief}", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    fireEvent.click(screen.getByRole("button", { name: /ig-2/i }));
    expect(recordIdeaSpy).toHaveBeenCalledWith({ id: "s1", idea_idx: 2, platform: "instagram", brief: "ig-2" });
  });

  it("test_flecha_best_effort · si use-idea lanza → la navegacion IGUAL ocurre", () => {
    recordIdeaSpy.mockImplementationOnce(() => { throw new Error("fail"); });
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    fireEvent.click(screen.getByRole("button", { name: /tt-1/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "tt-1", platform: "tiktok" } });
  });

  it("test_navega_con_idea · navega con el brief de ESA idea (Fase 0 preservado)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} />);
    fireEvent.click(screen.getByRole("button", { name: /ig-0/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "ig-0", platform: "instagram" } });
  });

  it("test_contador_quedan · 1 idea usada de 3 → '2 de 3 ideas disponibles' (las que quedan · C.1)", () => {
    render(<StrategyCard strategy={STRAT3} variant="active" usedCount={1} />);
    expect(screen.getByText(/2 de 3 ideas disponibles/i)).toBeTruthy();
  });

  it("test_contador_cero · sin ideas usadas → '3 de 3 ideas disponibles'", () => {
    render(<StrategyCard strategy={STRAT3} variant="active" usedCount={0} />);
    expect(screen.getByText(/3 de 3 ideas disponibles/i)).toBeTruthy();
  });
});
