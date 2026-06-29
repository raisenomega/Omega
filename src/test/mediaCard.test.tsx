// @vitest-environment jsdom
// Media C1 · extracción de MediaCard + thumbnail de video (primer frame vía <video src#t> · cero backend).
// Las imágenes siguen como <img>; los .mp4 ya no salen con ícono genérico. Acciones (overlay hover) intactas.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("react-router-dom", () => ({ useNavigate: () => vi.fn() }));
vi.mock("@/hooks/useBehavioralTracking", () => ({ useTrackOnMount: () => {} }));
vi.mock("@/contexts/ActiveBusinessContext", () => ({
  useActiveBusiness: () => ({ activeBusinessId: "biz1", isReady: true, setActiveBusiness: vi.fn() }),
}));
const IMG = { id: "1", name: "foto.png", metadata: { mimetype: "image/png", size: 2048 } };
const VID = { id: "2", name: "clip.mp4", metadata: { mimetype: "video/mp4", size: 1048576 } };
vi.mock("@/integrations/supabase/client", () => ({
  supabase: {
    auth: { getUser: vi.fn(async () => ({ data: { user: { id: "u1" } } })) },
    storage: {
      from: () => ({
        list: vi.fn(async () => ({ data: [IMG, VID], error: null })),
        getPublicUrl: (p: string) => ({ data: { publicUrl: `https://pub/${p}` } }),
        remove: vi.fn(async () => ({ error: null })),
      }),
    },
  },
}));

import { MediaCard } from "@/components/media/MediaCard";
import Media from "@/pages/Media";

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("MediaCard · thumbnail por tipo (C1)", () => {
  it("test_mediacard_imagen · imagen → <img> con la url pública", () => {
    const { container } = render(<MediaCard file={IMG} publicUrl="https://pub/foto.png" onDelete={() => {}} />, { wrapper: wrap });
    const img = container.querySelector("img");
    expect(img).toBeTruthy();
    expect(img!.getAttribute("src")).toBe("https://pub/foto.png");
  });
  it("test_mediacard_video · .mp4 → <video> con src #t (NO ícono genérico)", () => {
    const { container } = render(<MediaCard file={VID} publicUrl="https://pub/clip.mp4" onDelete={() => {}} />, { wrapper: wrap });
    const video = container.querySelector("video");
    expect(video).toBeTruthy();
    expect(video!.getAttribute("src")).toMatch(/#t=/);          // primer frame como preview
    expect(container.querySelector("img")).toBeNull();          // no es imagen
  });
  it("test_mediacard_nombre_size · muestra nombre + tamaño", () => {
    const { getByText } = render(<MediaCard file={IMG} publicUrl="https://pub/foto.png" onDelete={() => {}} />, { wrapper: wrap });
    expect(getByText("foto.png")).toBeTruthy();
    expect(getByText(/2 KB/)).toBeTruthy();                     // formatBytes(2048)
  });
});

describe("Media · renderiza las tarjetas vía MediaCard (C1)", () => {
  it("test_media_usa_mediacard · grid con imagen + video sin regresión", async () => {
    const { findByText, container } = render(<Media />, { wrapper: wrap });
    expect(await findByText("foto.png")).toBeTruthy();
    expect(await findByText("clip.mp4")).toBeTruthy();
    expect(container.querySelector("video")).toBeTruthy();      // el .mp4 ahora con preview real
  });
});
