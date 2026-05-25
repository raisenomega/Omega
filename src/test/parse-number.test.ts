// FIX 2 · blinda el parseo de campos numéricos con formato libre del wizard.
import { describe, it, expect } from "vitest";
import { parseLooseNumber } from "@/lib/parse-number";

describe("parseLooseNumber", () => {
  it("quita comas / puntos / espacios → número", () => {
    expect(parseLooseNumber("10,000")).toBe(10000);
    expect(parseLooseNumber("1.500")).toBe(1500);
    expect(parseLooseNumber("10 000")).toBe(10000);
    expect(parseLooseNumber("42")).toBe(42);
  });
  it("vacío / solo espacios / no numérico → null", () => {
    expect(parseLooseNumber("")).toBeNull();
    expect(parseLooseNumber("   ")).toBeNull();
    expect(parseLooseNumber("abc")).toBeNull();
  });
});
