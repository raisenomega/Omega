// Cliente PYME ve la pestaña Aprendizaje: cero jerga técnica · español de negocio.
// Cubre el mapeo crudo→ES, el fallback legible, y que parseRaw no descarte filas sin evaluated_at.
import { describe, it, expect } from "vitest";
import { labelDecision, labelOutcome, labelAgent, isInternalErrorDecision } from "@/lib/learning-labels";
import { parseRaw, buildLearningEvents } from "@/hooks/learning-events-data";

describe("learning-labels · español de negocio", () => {
  it("decision: crudos conocidos → etiqueta ES", () => {
    expect(labelDecision("generated_not_saved")).toBe("Propuse contenido que no se usó");
    expect(labelDecision("approved_by_client")).toBe("Acertó: contenido aprobado");
  });

  it("error interno [failed:...] se detecta para excluir (no es aprendizaje)", () => {
    expect(isInternalErrorDecision("[failed:api_error]")).toBe(true);
    expect(isInternalErrorDecision("[failed:timeout]")).toBe(true);
    expect(isInternalErrorDecision("approved_by_client")).toBe(false);
  });

  it("decision: completion=NN% → 'Perfil completado al NN%'", () => {
    expect(labelDecision("completion=90%")).toBe("Perfil completado al 90%");
    expect(labelDecision("completion=80%")).toBe("Perfil completado al 80%");
  });

  it("decision: texto natural pasa tal cual", () => {
    expect(labelDecision("Datos del cliente actualizados")).toBe("Datos del cliente actualizados");
  });

  it("decision: crudo desconocido → fallback legible (cero snake_case)", () => {
    const out = labelDecision("some_new_event_type");
    expect(out).not.toContain("_");
    expect(out).toBe("Some new event type");
  });

  it("agent: nova→'Tu asistente' (NO expone NOVA), aria→ARIA", () => {
    expect(labelAgent("nova")).toBe("Tu asistente");
    expect(labelAgent("aria")).toBe("ARIA");
    expect(labelAgent("brand_voice")).toBe("Voz de marca");
    expect(labelAgent("content_creator")).toBe("Creador de contenido");
  });

  it("agent: code sin etiqueta ES → nombre de tabla si existe, si no humanize (nunca snake_case)", () => {
    expect(labelAgent("xyz_agent", "Nombre Tabla")).toBe("Nombre Tabla");
    expect(labelAgent("xyz_agent")).toBe("Xyz agent");
  });

  it("outcome: draft_abandoned_72h → ES, null → null", () => {
    expect(labelOutcome("draft_abandoned_72h")).toBe("Borrador no publicado en 72h");
    expect(labelOutcome(null)).toBeNull();
  });
});

describe("parseRaw · evaluated_at nullable (bug del 0%)", () => {
  const base = { id: "1", agent_code: "brand_voice", decision: "approved_by_client",
    was_correct: true, confidence: 10, outcome: null };

  it("fila con was_correct pero SIN evaluated_at NO se descarta", () => {
    const r = parseRaw({ ...base, evaluated_at: null });
    expect(r).not.toBeNull();
    expect(r?.was_correct).toBe(true);
    expect(r?.evaluated_at).toBeNull();
  });

  it("buildLearningEvents cuenta las acertadas sin evaluated_at + traduce a ES", () => {
    const rows = [
      { ...base, id: "a", was_correct: true, evaluated_at: null },
      { ...base, id: "b", was_correct: false, decision: "generated_not_saved", evaluated_at: "2026-06-01T00:00:00Z" },
    ];
    const r = buildLearningEvents(rows, [{ code: "brand_voice", name: "Brand Voice Agent" }]);
    expect(r.correctCount).toBe(1);   // la acertada sin fecha SÍ cuenta (era el bug)
    expect(r.incorrectCount).toBe(1);
    expect(r.accuracy).toBe(50);
    expect(r.events[0].agentName).toBe("Voz de marca");        // ES, no "Brand Voice Agent" ni code
    expect(r.events[0].decision).toBe("Acertó: contenido aprobado");
  });

  it("excluye [failed:...] del denominador y de los eventos (plomería, no aprendizaje)", () => {
    const rows = [
      { ...base, id: "ok", was_correct: true, evaluated_at: "2026-06-01T00:00:00Z" },
      { ...base, id: "err1", was_correct: false, decision: "[failed:api_error]", evaluated_at: "2026-06-01T00:00:00Z" },
      { ...base, id: "err2", was_correct: false, decision: "[failed:timeout]", evaluated_at: "2026-06-01T00:00:00Z" },
    ];
    const r = buildLearningEvents(rows, []);
    expect(r.events).toHaveLength(1);          // los 2 errores fuera
    expect(r.correctCount).toBe(1);
    expect(r.incorrectCount).toBe(0);          // los failed NO cuentan como incorrectas
    expect(r.accuracy).toBe(100);              // 1/1, no 1/3
  });
});
