// HERMES tab · labels §8 · cero jerga técnica en pantalla (panel del super_owner).
import { describe, it, expect } from "vitest";
import { effectiveStatus, integrationLabel, integrationUrl, statusInfo } from "@/components/security-dev/hermes-labels";

const agoMin = (m: number) => new Date(Date.now() - m * 60000).toISOString();

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

describe("hermes-labels · semáforo amarillo derivado + links", () => {
  it("ok + last_use reciente → ok (verde)", () => {
    expect(effectiveStatus({ integration: "anthropic", status: "ok", last_use: agoMin(30) })).toBe("ok");
  });

  it("ok + last_use más viejo que el umbral por integración → sin_uso_reciente (amarillo)", () => {
    expect(effectiveStatus({ integration: "anthropic", status: "ok", last_use: agoMin(90) })).toBe("sin_uso_reciente"); // anthropic 60m
    expect(effectiveStatus({ integration: "veo3", status: "ok", last_use: agoMin(90) })).toBe("ok");                    // veo3 21d → 90m sigue ok
  });

  it("ok + sin last_use → sin_uso (gris · ausencia de señal, NO amarillo)", () => {
    expect(effectiveStatus({ integration: "anthropic", status: "ok", last_use: null })).toBe("sin_uso");
  });

  it("estados no-ok pasan tal cual (failed/no_configurado mandan)", () => {
    expect(effectiveStatus({ integration: "brave", status: "last_use_failed", last_use: null })).toBe("last_use_failed");
    expect(effectiveStatus({ integration: "brave", status: "no_configurado", last_use: null })).toBe("no_configurado");
  });

  it("orden de severidad: amarillo < operativo < gris", () => {
    expect(statusInfo("sin_uso_reciente").rank).toBeLessThan(statusInfo("ok").rank);
    expect(statusInfo("ok").rank).toBeLessThan(statusInfo("sin_uso").rank);
  });

  it("link de proveedor: conocido → URL https, desconocido → null", () => {
    expect(integrationUrl("anthropic")).toBe("https://console.anthropic.com");
    expect(integrationUrl("nano_banana")).toContain("aistudio.google.com");
    expect(integrationUrl("inexistente")).toBeNull();
  });
});
