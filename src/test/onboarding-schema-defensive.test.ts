// BUG A · blinda el fix defensivo: data legacy/inválida NUNCA debe lanzar en parse
// (lo que dispararía onInvalid y bloquearía el save del wizard al editar cliente).
import { describe, it, expect } from "vitest";
import { onboardingSchema } from "@/lib/onboarding-schema";
import { audienceSchema, brandVoiceSchema, brandAssetsSchema } from "@/lib/onboarding-schema-sections";
import { INDUSTRIES } from "@/lib/client-constants";
import { REGIONS } from "@/lib/client-constants";

describe("onboarding schema · BUG A defensivo", () => {
  it("competitors legacy string[] → {name,url}[]", () => {
    const r = audienceSchema.parse({ competitors: ["Comp A", "Comp B"] });
    expect(r.competitors).toEqual([
      { name: "Comp A", url: null },
      { name: "Comp B", url: null },
    ]);
  });

  it("hex/uuid inválidos → null (no lanza)", () => {
    const r = brandAssetsSchema.parse({ primary_color: "blue", logo_file_id: "not-a-uuid" });
    expect(r.primary_color).toBeNull();
    expect(r.logo_file_id).toBeNull();
  });

  it("enum drift: array → [] · single → null", () => {
    const r = brandVoiceSchema.parse({ tone: ["inexistente"], emoji_usage: "??" });
    expect(r.tone).toEqual([]);
    expect(r.emoji_usage).toBeNull();
  });

  it("parse completo con data stale NO lanza · lo válido se conserva", () => {
    const stale = {
      identity: { name: "La Milagrosa", industry: INDUSTRIES[0], regions: [REGIONS[0]] },
      business: { business_size: "gigante_invalido" },
      audience: { competitors: ["X"], audience_gender: "alien" },
      brand_voice: { tone: ["raro"], preferred_formats: ["mal"], hashtag_strategy: "??" },
      goals: { primary_goal: ["zzz"] },
      brand_assets: { primary_color: "red", brand_guide_file_id: "x" },
    };
    expect(() => onboardingSchema.parse(stale)).not.toThrow();
    const parsed = onboardingSchema.parse(stale);
    expect(parsed.identity.name).toBe("La Milagrosa");
    expect(parsed.business.business_size).toBeNull();
    expect(parsed.brand_voice.tone).toEqual([]);
    expect(parsed.audience.competitors).toEqual([{ name: "X", url: null }]);
  });
});
