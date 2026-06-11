import { describe, it, expect } from "vitest";
import { brandVoiceScheduleError } from "@/lib/schedule-error";

describe("brandVoiceScheduleError", () => {
  it("no es error de voz de marca → null (cae al toast genérico)", () => {
    expect(brandVoiceScheduleError("content_not_found:abc")).toBeNull();
    expect(brandVoiceScheduleError("HTTP 500")).toBeNull();
  });

  it("422 un solo contenido → singular", () => {
    const r = brandVoiceScheduleError("brand_voice_below_threshold:c1=0.42");
    expect(r).not.toBeNull();
    expect(r?.description).toContain("Este contenido no pasa");
    expect(r?.description).toContain("score < 0.7");
  });

  it("422 varios contenidos → cuenta cuántos fallaron (Ajuste 1)", () => {
    const r = brandVoiceScheduleError("brand_voice_below_threshold:c1=0.42,c2=0.30,c3=0.10");
    expect(r?.description).toContain("3 contenidos no pasan");
  });

  it("503 unavailable → mensaje honesto sin filtrar el param force al usuario", () => {
    const r = brandVoiceScheduleError("brand_voice_check_unavailable · usa force_brand_voice=true ...");
    expect(r).not.toBeNull();
    expect(r?.description).not.toContain("force_brand_voice");
  });
});
