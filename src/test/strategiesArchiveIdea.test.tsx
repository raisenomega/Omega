// @vitest-environment jsdom
// Fase C.2 Commit 2 (frontend) · IdeaUsageCard en Usadas gana "Archivar" (PATCH .../archive → la
// idea sale de Usadas). El chip "Archivadas" pasa a mostrar IDEAS archivadas (used-ideas?archived=true)
// en vez de estrategias (cambio de semantica · modelo idea-level). Las idea-cards de Archivadas NO
// tienen boton aun (Eliminar = C.3). Solo frontend · el endpoint ya existe (C.2 backend).
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const archiveSpy = vi.fn();
vi.mock("@/hooks/useArchiveIdea", () => ({ useArchiveIdea: () => ({ mutate: archiveSpy, isPending: false }) }));
vi.mock("@/hooks/useDeleteIdea", () => ({ useDeleteIdea: () => ({ mutate: vi.fn(), isPending: false }) }));

import { IdeaUsageCard } from "@/components/strategies/IdeaUsageCard";
import type { UsedIdea } from "@/hooks/useUsedIdeas";

const IDEA: UsedIdea = {
  id: "u1", strategy_id: "s1", client_id: "biz1", idea_idx: 0, platform: "instagram",
  brief: "texto de la idea", used_at: "2026-06-10T00:00:00Z", strategies: { titulo: "Mi estrategia" },
};

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("Fase C.2 Commit 2 · Archivar idea + Archivadas = ideas", () => {
  it("test_usadas_archivar_botones · en Usadas (archived=false) la card muestra 'Re-usar' + 'Archivar'", () => {
    render(<IdeaUsageCard idea={IDEA} archived={false} />);
    expect(screen.getByRole("button", { name: /re-?usar/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /archivar/i })).toBeTruthy();
  });

  it("test_archivar_llama · click 'Archivar' → useArchiveIdea con el id de la idea-usage", () => {
    render(<IdeaUsageCard idea={IDEA} archived={false} />);
    fireEvent.click(screen.getByRole("button", { name: /archivar/i }));
    expect(archiveSpy).toHaveBeenCalledWith({ id: "u1" });
  });

  it("test_archivadas_solo_eliminar · en Archivadas (archived=true) la card tiene Eliminar (no Re-usar/Archivar)", () => {
    render(<IdeaUsageCard idea={IDEA} archived={true} />);
    expect(screen.queryByRole("button", { name: /re-?usar/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /archivar/i })).toBeNull();
    expect(screen.getByRole("button", { name: /eliminar/i })).toBeTruthy();   // C.3 · solo Eliminar
    expect(screen.getByText("texto de la idea")).toBeTruthy();
  });

  it("test_reusar_sigue · 'Re-usar' en Usadas sigue navegando (cero regresion)", () => {
    render(<IdeaUsageCard idea={IDEA} archived={false} />);
    fireEvent.click(screen.getByRole("button", { name: /re-?usar/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "texto de la idea", platform: "instagram" } });
  });
});
