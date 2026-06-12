import { describe, it, expect } from "vitest";
import { brandVoiceScheduleError } from "@/lib/schedule-error";

describe("brandVoiceScheduleError", () => {
  it("no es error de voz de marca → null (cae al toast genérico)", () => {
    expect(brandVoiceScheduleError("content_not_found:abc")).toBeNull();
    expect(brandVoiceScheduleError("HTTP 500")).toBeNull();
  });

  it("422 daño · un solo contenido → singular (mensaje de DAÑO, no <0.7)", () => {
    const r = brandVoiceScheduleError("brand_voice_damages_brand:c1=0.15");
    expect(r).not.toBeNull();
    expect(r?.description).toContain("Este contenido daña");
    expect(r?.description).toContain("insultos, spam");
    expect(r?.description).not.toContain("0.7");   // el 422 ya no significa "bajo el bar"
  });

  it("422 daño · varios contenidos → cuenta cuántos (Ajuste 1)", () => {
    const r = brandVoiceScheduleError("brand_voice_damages_brand:c1=0.15,c2=0.10,c3=0.05");
    expect(r?.description).toContain("3 contenidos dañan");
  });

  it("503 unavailable → mensaje honesto sin filtrar el param force al usuario", () => {
    const r = brandVoiceScheduleError("brand_voice_check_unavailable · usa force_brand_voice=true ...");
    expect(r).not.toBeNull();
    expect(r?.description).not.toContain("force_brand_voice");
  });
});
