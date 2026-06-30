// @vitest-environment jsdom
// Fase C.3 Commit 2 (frontend) · en Archivadas cada idea-card gana "Eliminar" → ⚠️ abre un
// AlertDialog de confirmacion ("¿Eliminar para siempre?") · SOLO al confirmar borra (DELETE
// /used-ideas/{id}). Cancelar no hace nada. Usadas NO tiene Eliminar. El confirm es OBLIGATORIO.
import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup, within } from "@testing-library/react";

const deleteSpy = vi.fn();
vi.mock("@/hooks/useDeleteIdea", () => ({ useDeleteIdea: () => ({ mutate: deleteSpy, isPending: false }) }));
vi.mock("@/hooks/useArchiveIdea", () => ({ useArchiveIdea: () => ({ mutate: vi.fn(), isPending: false }) }));
vi.mock("react-router-dom", () => ({ useNavigate: () => vi.fn() }));

import { IdeaUsageCard } from "@/components/strategies/IdeaUsageCard";
import type { UsedIdea } from "@/hooks/useUsedIdeas";

const IDEA: UsedIdea = {
  id: "u1", strategy_id: "s1", client_id: "biz1", idea_idx: 0, platform: "instagram",
  brief: "texto", used_at: "2026-06-10T00:00:00Z", strategies: { titulo: "T" },
};

beforeAll(() => {
  Element.prototype.hasPointerCapture = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("Fase C.3 Commit 2 · Eliminar idea con confirm obligatorio", () => {
  it("test_archivadas_boton_eliminar · idea-card en Archivadas muestra 'Eliminar'", () => {
    render(<IdeaUsageCard idea={IDEA} archived={true} />);
    expect(screen.getByRole("button", { name: /eliminar/i })).toBeTruthy();
  });

  it("test_usadas_sin_eliminar · idea-card en Usadas NO muestra 'Eliminar'", () => {
    render(<IdeaUsageCard idea={IDEA} archived={false} />);
    expect(screen.queryByRole("button", { name: /eliminar/i })).toBeNull();
  });

  it("test_eliminar_abre_confirm · click 'Eliminar' → abre el confirm (NO borra directo)", () => {
    render(<IdeaUsageCard idea={IDEA} archived={true} />);
    fireEvent.click(screen.getByRole("button", { name: /eliminar/i }));
    expect(screen.getByText(/eliminar para siempre/i)).toBeTruthy();   // el AlertDialog aparecio
    expect(deleteSpy).not.toHaveBeenCalled();                          // ⚠️ NO borra con un solo clic
  });

  it("test_confirm_borra · confirmar en el dialog → useDeleteIdea con {id}", () => {
    render(<IdeaUsageCard idea={IDEA} archived={true} />);
    fireEvent.click(screen.getByRole("button", { name: /eliminar/i }));
    const dialog = screen.getByRole("alertdialog");
    fireEvent.click(within(dialog).getByRole("button", { name: /^eliminar$/i }));
    expect(deleteSpy).toHaveBeenCalledWith({ id: "u1" });
  });

  it("test_cancelar_no_borra · cancelar → NO llama useDeleteIdea (la idea sigue)", () => {
    render(<IdeaUsageCard idea={IDEA} archived={true} />);
    fireEvent.click(screen.getByRole("button", { name: /eliminar/i }));
    fireEvent.click(within(screen.getByRole("alertdialog")).getByRole("button", { name: /cancelar/i }));
    expect(deleteSpy).not.toHaveBeenCalled();
  });
});
