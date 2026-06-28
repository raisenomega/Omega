// @vitest-environment jsdom
// H2 · descargar un carrusel baja las N imágenes (placa-1.png … placa-N.png), NO 1 .txt del título.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { downloadResult } from "@/lib/download-result";
import type { ResultV2 } from "@/components/content/result-types";

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({ ok: true, blob: () => Promise.resolve(new Blob(["x"], { type: "image/png" })) })));
  vi.stubGlobal("URL", { createObjectURL: () => "blob:x", revokeObjectURL: () => {} });
});
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

const CAROUSEL: ResultV2 = {
  id: "c1", content_type: "carousel", generated_text: "Título",
  media_urls: ["https://s/0.png", "https://s/1.png", "https://s/2.png"],
};

describe("downloadResult · carrusel (H2)", () => {
  it("descarga las N imágenes sueltas (no 1 .txt)", async () => {
    const names: string[] = [];
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) { names.push(this.download); });
    await downloadResult(CAROUSEL);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(3);
    expect(vi.mocked(fetch).mock.calls.map(c => String(c[0]))).toEqual(["https://s/0.png", "https://s/1.png", "https://s/2.png"]);
    expect(names).toEqual(["placa-1.png", "placa-2.png", "placa-3.png"]);  // N sueltos, nombrados por placa
  });
});
