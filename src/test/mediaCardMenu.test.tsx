// @vitest-environment jsdom
// Media C2 · las 4 acciones se REUBICAN del overlay hover a un botón [Ver] (color primary · marca)
// que abre un mini-menú (DropdownMenu). Cero backend: los handlers son los mismos del C1, solo
// cambian de contenedor (overlay → menú). "Usar en Content Lab" sigue solo para imágenes.
import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const toastSpy = vi.fn();
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: toastSpy }) }));

import { MediaCardMenu } from "@/components/media/MediaCardMenu";
import { MediaCard } from "@/components/media/MediaCard";

// Radix DropdownMenu usa pointer capture + scrollIntoView (no implementados en jsdom).
beforeAll(() => {
  Element.prototype.hasPointerCapture = vi.fn();
  Element.prototype.releasePointerCapture = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});
beforeEach(() => {
  vi.clearAllMocks();
  Object.assign(navigator, { clipboard: { writeText: vi.fn(async () => {}) } });
  vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, blob: async () => new Blob(["x"]) })));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

function openMenu() {
  // jsdom no implementa PointerEvent.button → Radix abre por teclado de forma fiable.
  const trigger = screen.getByRole("button", { name: /más opciones/i });
  fireEvent.keyDown(trigger, { key: "Enter" });
  return trigger;
}

describe("MediaCardMenu · botón ⋮ (más opciones) + mini-menú (C2)", () => {
  it("test_trigger_button · botón ⋮ visible (aria-label) con color primary", () => {
    render(<MediaCardMenu fileName="foto.png" publicUrl="https://pub/foto.png" isImage onDelete={() => {}} />);
    const trigger = screen.getByRole("button", { name: /más opciones/i });
    expect(trigger).toBeTruthy();
    expect(trigger.className).toMatch(/bg-primary/);                 // amarillo de marca, no verde
    expect(trigger.className).toMatch(/text-primary-foreground/);
  });

  it("test_ver_abre_menu · click en [Ver] → 4 items (imagen)", () => {
    render(<MediaCardMenu fileName="foto.png" publicUrl="https://pub/foto.png" isImage onDelete={() => {}} />);
    openMenu();
    expect(screen.getByText("Copiar")).toBeTruthy();
    expect(screen.getByText("Usar en Content Lab")).toBeTruthy();
    expect(screen.getByText("Descargar")).toBeTruthy();
    expect(screen.getByText("Eliminar")).toBeTruthy();
  });

  it("test_menu_acciones · cada item llama su handler existente", async () => {
    const onDelete = vi.fn();
    render(<MediaCardMenu fileName="foto.png" publicUrl="https://pub/foto.png" isImage onDelete={onDelete} />);
    openMenu();
    fireEvent.click(screen.getByText("Copiar"));
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://pub/foto.png");

    openMenu();
    fireEvent.click(screen.getByText("Usar en Content Lab"));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { referenceImageUrl: "https://pub/foto.png" } });

    openMenu();
    fireEvent.click(screen.getByText("Descargar"));
    expect(fetch).toHaveBeenCalledWith("https://pub/foto.png");

    openMenu();
    fireEvent.click(screen.getByText("Eliminar"));
    expect(onDelete).toHaveBeenCalledWith("foto.png");
  });

  it("test_usar_solo_imagen · 'Usar en Content Lab' NO aparece en video", () => {
    render(<MediaCardMenu fileName="clip.mp4" publicUrl="https://pub/clip.mp4" isImage={false} onDelete={() => {}} />);
    openMenu();
    expect(screen.getByText("Copiar")).toBeTruthy();
    expect(screen.getByText("Descargar")).toBeTruthy();
    expect(screen.getByText("Eliminar")).toBeTruthy();
    expect(screen.queryByText("Usar en Content Lab")).toBeNull();   // solo imágenes, como hoy
  });
});

describe("MediaCard · ya NO usa overlay hover de acciones (C2)", () => {
  const IMG = { id: "1", name: "foto.png", metadata: { mimetype: "image/png", size: 2048 } };
  it("test_no_overlay · sin overlay group-hover de acciones, con botón ⋮", () => {
    const { container } = render(<MediaCard file={IMG} publicUrl="https://pub/foto.png" onDelete={() => {}} />);
    expect(container.querySelector('[class*="group-hover:opacity-100"]')).toBeNull();
    expect(screen.getByRole("button", { name: /más opciones/i })).toBeTruthy();
  });
});
