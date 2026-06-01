// HERMES tab · labels §8 · cero jerga técnica en pantalla (panel del super_owner).
import { describe, it, expect } from "vitest";
import { integrationLabel, statusInfo } from "@/components/security-dev/hermes-labels";

describe("hermes-labels · §8 español de negocio", () => {
  it("integraciones conocidas → nombre legible", () => {
    expect(integrationLabel("anthropic")).toBe("Anthropic (texto/ARIA)");
    expect(integrationLabel("nano_banana")).toBe("Generación de imágenes");
    expect(integrationLabel("veo3")).toBe("Generación de video");
    expect(integrationLabel("voyage")).toBe("Memoria semántica");
    expect(integrationLabel("stripe")).toBe("Pagos");
  });

  it("integración desconocida → humanize (cero snake_case)", () => {
    const out = integrationLabel("new_mcp_thing");
    expect(out).not.toContain("_");
    expect(out).toBe("New mcp thing");
  });

  it("estados → label ES + rank de orden (fallido arriba)", () => {
    expect(statusInfo("ok").label).toBe("Operativo");
    expect(statusInfo("no_configurado").label).toBe("Sin configurar");
    expect(statusInfo("last_use_failed").label).toBe("Falló el último uso");
    // rank: fallido (0) < operativo (1) < sin configurar (2)
    expect(statusInfo("last_use_failed").rank).toBeLessThan(statusInfo("ok").rank);
    expect(statusInfo("ok").rank).toBeLessThan(statusInfo("no_configurado").rank);
  });

  it("estado desconocido → humanize, no snake_case", () => {
    const s = statusInfo("weird_state");
    expect(s.label).not.toContain("_");
  });
});
