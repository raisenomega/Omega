import { describe, it, expect } from "vitest";
import { toUtcIso } from "@/lib/schedule-time";

describe("toUtcIso (bug tz 11 jun)", () => {
  it("local naive → UTC ISO con Z, mismo instante (tz-independiente)", () => {
    const local = "2026-06-13T13:00";
    const utc = toUtcIso(local);
    expect(utc.endsWith("Z")).toBe(true);                              // UTC explícito
    expect(new Date(utc).getTime()).toBe(new Date(local).getTime());   // mismo instante
  });

  it("acepta el string con segundos", () => {
    expect(toUtcIso("2026-06-13T13:00:00").endsWith("Z")).toBe(true);
  });
});
