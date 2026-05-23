import type { ResultV2 } from "@/components/content/ResultCardV2";

const LS_KEY = "omega_content_lab_results";
const MAX_PERSISTED = 20;

export function loadPersistedResults(): ResultV2[] {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function persistResults(results: ResultV2[]): void {
  try {
    const completed = results.filter(r => r.status !== "pending");
    const recent = completed.slice(-MAX_PERSISTED);
    localStorage.setItem(LS_KEY, JSON.stringify(recent));
  } catch {
    // localStorage full/disabled/private mode · silent skip
  }
}
