// DEBT-102 · helpers puros del widget Learning Events (sin I/O · testeables).
// parseRaw narrow defensivo desde unknown (cero any) + buildLearningEvents agrega
// conteos/accuracy idéntico a aria_learning_report._aggregate (DEBT-101).

export interface LearningEvent {
  id: string;
  agentName: string;          // resuelto desde agents.name (o agent_code fallback)
  decision: string;           // qué decidió ARIA
  outcome: string | null;     // qué resultó
  was_correct: boolean;       // garantizado non-null (filtrado en query)
  confidence: number;
  evaluated_at: string;       // ISO · fecha de evaluación
}

interface RawEvent {
  id: string;
  agent_code: string;
  decision: string;
  outcome: string | null;
  was_correct: boolean;
  confidence: number;
  evaluated_at: string;
}

export function parseRaw(row: unknown): RawEvent | null {
  if (typeof row !== "object" || row === null) return null;
  const r = row as Record<string, unknown>;
  if (typeof r.id !== "string" || typeof r.agent_code !== "string") return null;
  if (typeof r.decision !== "string" || typeof r.was_correct !== "boolean") return null;
  if (typeof r.confidence !== "number") return null;
  if (typeof r.evaluated_at !== "string") return null;
  return {
    id: r.id,
    agent_code: r.agent_code,
    decision: r.decision,
    outcome: typeof r.outcome === "string" ? r.outcome : null,
    was_correct: r.was_correct,
    confidence: r.confidence,
    evaluated_at: r.evaluated_at,
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
    const { agent_code, ...rest } = p;
    return [{ ...rest, agentName: nameMap.get(agent_code) ?? agent_code }];
  });
  const correctCount = events.filter((e) => e.was_correct).length;
  const incorrectCount = events.length - correctCount;
  const accuracy = events.length > 0 ? Math.round((100 * correctCount) / events.length) : null;
  return { events, correctCount, incorrectCount, accuracy };
}
