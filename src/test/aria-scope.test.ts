// Switcher V1 · ARIA scope por negocio activo (DEBT-ARIA-CHAT-CLIENT-ID).
// Lógica pura usada por useARIAChat + ARIASection: activo → client_id; sin activo → legacy.
import { describe, it, expect } from "vitest";
import { ariaHistoryQuery, ariaMessageBody, ariaHistoryKey } from "@/lib/aria-scope";

describe("aria-scope · Switcher V1", () => {
  it("history query: activo → ?client_id, sin activo → vacío (legacy)", () => {
    expect(ariaHistoryQuery("biz-A")).toBe("?client_id=biz-A");
    expect(ariaHistoryQuery(null)).toBe("");
  });

  it("history query encodea ids con caracteres especiales", () => {
    expect(ariaHistoryQuery("a/b c")).toBe(`?client_id=${encodeURIComponent("a/b c")}`);
  });

  it("message body: activo incluye client_id, sin activo no lo manda (legacy)", () => {
    expect(ariaMessageBody("hola", "biz-A")).toEqual({ content: "hola", client_id: "biz-A" });
    expect(ariaMessageBody("hola", null)).toEqual({ content: "hola" });
    expect("client_id" in ariaMessageBody("hola", null)).toBe(false);
  });

  it("queryKey incluye activeBusinessId → cache invalida al cambiar negocio", () => {
    expect(ariaHistoryKey("biz-A")).toEqual(["aria_history", "biz-A"]);
    expect(ariaHistoryKey("biz-B")).toEqual(["aria_history", "biz-B"]);
    expect(ariaHistoryKey(null)).toEqual(["aria_history", null]);
  });
});
