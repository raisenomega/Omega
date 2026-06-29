// @vitest-environment jsdom
// Media C3 · click en el thumbnail (NO en [Ver]) abre un pop-up de preview (Dialog).
// Imagen → <img object-contain max-h-[90vh]> completa sin scroll. Video → <video controls> que
// reproduce (no solo el primer frame). El click en [Ver] sigue abriendo el menú, NO el preview
// (zonas separadas: thumbnail = preview · franja inferior [Ver] = menú). Cero backend.
import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

vi.mock("react-router-dom", () => ({ useNavigate: () => vi.fn() }));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));

import { MediaCard } from "@/components/media/MediaCard";

const IMG = { id: "1", name: "foto.png", metadata: { mimetype: "image/png", size: 2048 } };
const VID = { id: "2", name: "clip.mp4", metadata: { mimetype: "video/mp4", size: 1048576 } };

beforeAll(() => {
  Element.prototype.hasPointerCapture = vi.fn();
  Element.prototype.releasePointerCapture = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("MediaCard · click en thumbnail → preview modal (C3)", () => {
  it("test_click_imagen_abre_modal · click en imagen → modal con <img>", () => {
    const { container } = render(<MediaCard file={IMG} publicUrl="https://pub/foto.png" onDelete={() => {}} />);
    fireEvent.click(container.querySelector("img")!);               // thumbnail
    const dialog = screen.getByRole("dialog");
    const img = dialog.querySelector("img");
    expect(img).toBeTruthy();
    expect(img!.getAttribute("src")).toBe("https://pub/foto.png");
  });

  it("test_click_video_abre_modal · click en video → modal con <video controls>", () => {
    const { container } = render(<MediaCard file={VID} publicUrl="https://pub/clip.mp4" onDelete={() => {}} />);
    fireEvent.click(container.querySelector("video")!);             // thumbnail
    const dialog = screen.getByRole("dialog");
    const video = dialog.querySelector("video");
    expect(video).toBeTruthy();
    expect(video!.hasAttribute("controls")).toBe(true);            // reproduce, no solo frame
  });

  it("test_modal_imagen_contain · imagen usa object-contain max-h (sin scroll)", () => {
    const { container } = render(<MediaCard file={IMG} publicUrl="https://pub/foto.png" onDelete={() => {}} />);
    fireEvent.click(container.querySelector("img")!);
    const img = screen.getByRole("dialog").querySelector("img")!;
    expect(img.className).toMatch(/object-contain/);
    expect(img.className).toMatch(/max-h-\[90vh\]/);
  });

  it("test_modal_video_reproduce · el modal de video tiene controls", () => {
    const { container } = render(<MediaCard file={VID} publicUrl="https://pub/clip.mp4" onDelete={() => {}} />);
    fireEvent.click(container.querySelector("video")!);
    const video = screen.getByRole("dialog").querySelector("video")!;
    expect(video.hasAttribute("controls")).toBe(true);
    expect(video.getAttribute("src")).toBe("https://pub/clip.mp4");  // url limpia, sin #t
  });

  it("test_ver_no_abre_preview · click en [Ver] abre el menú, NO el preview", () => {
    render(<MediaCard file={IMG} publicUrl="https://pub/foto.png" onDelete={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /ver/i }));   // franja inferior
    expect(screen.queryByRole("dialog")).toBeNull();                // zonas separadas
  });
});
