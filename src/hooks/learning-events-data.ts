// DEBT-102 · helpers puros del widget Learning Events (sin I/O · testeables).
// parseRaw narrow defensivo desde unknown (cero any) + buildLearningEvents agrega
// conteos/accuracy idéntico a aria_learning_report._aggregate (DEBT-101).
// Render en español de negocio vía learning-labels (cero jerga técnica al cliente).

import { labelDecision, labelOutcome, labelAgent, isInternalErrorDecision } from "@/lib/learning-labels";

export interface LearningEvent {
  id: string;
  agentName: string;          // resuelto desde agents.name (o agent_code fallback)
  decision: string;           // qué decidió ARIA
  outcome: string | null;     // qué resultó
  was_correct: boolean;       // garantizado non-null (filtrado en query)
  confidence: number;
  evaluated_at: string | null; // ISO · fecha de evaluación · NULL si la señal vino directa (sin cron)
}

interface RawEvent {
  id: string;
  agent_code: string;
  decision: string;
  outcome: string | null;
  was_correct: boolean;
  confidence: number;
  evaluated_at: string | null;
}

export function parseRaw(row: unknown): RawEvent | null {
  if (typeof row !== "object" || row === null) return null;
  const r = row as Record<string, unknown>;
  if (typeof r.id !== "string" || typeof r.agent_code !== "string") return null;
  if (typeof r.decision !== "string" || typeof r.was_correct !== "boolean") return null;
  if (typeof r.confidence !== "number") return null;
  // evaluated_at es OPCIONAL (igual que outcome): es la fecha en que el cron tocó la fila, no la
  // señal. Una fila con was_correct real puede nacer sin cron (brand_voice/nova · veredicto directo)
  // → evaluated_at NULL. Exigirlo descartaba las acertadas y mostraba 0% (bug). Solo se requiere la
  // señal (was_correct bool), no el timestamp.
  return {
    id: r.id,
    agent_code: r.agent_code,
    decision: r.decision,
    outcome: typeof r.outcome === "string" ? r.outcome : null,
    was_correct: r.was_correct,
    confidence: r.confidence,
    evaluated_at: typeof r.evaluated_at === "string" ? r.evaluated_at : null,
  };
}

export interface LearningSummary {
  events: LearningEvent[];
  correctCount: number;
  incorrectCount: number;
  accuracy: number | null;    // % entero · null si no hay evaluados
}

export function buildLearningEvents(
  rawRows: unknown[],
  agentRows: { code: string; name: string }[]
): LearningSummary {
  const nameMap = new Map<string, string>(agentRows.map((a) => [a.code, a.name]));
  const events: LearningEvent[] = rawRows.flatMap((row) => {
    const p = parseRaw(row);
    if (!p) return [];
    if (isInternalErrorDecision(p.decision)) return [];  // fallo de API/infra · no es aprendizaje (excluido del denominador)
    const { agent_code, decision, outcome, ...rest } = p;
    // agentName: etiqueta ES de negocio (labelAgent · cubre nova/aria + códigos conocidos); si el
    // code no tiene etiqueta ES, usar el nombre de la tabla agents; si tampoco, humanize. NUNCA
    // agent_code crudo. decision/outcome también en español de negocio.
    return [{
      ...rest,
      agentName: labelAgent(agent_code, nameMap.get(agent_code)),
      decision: labelDecision(decision),
      outcome: labelOutcome(outcome),
    }];
  });
  const correctCount = events.filter((e) => e.was_correct).length;
  const incorrectCount = events.length - correctCount;
  const accuracy = events.length > 0 ? Math.round((100 * correctCount) / events.length) : null;
  return { events, correctCount, incorrectCount, accuracy };
}
