// Switcher V1: construcción del scope ARIA por negocio activo. Lógica pura (testeable sin DOM)
// extraída de useARIAChat + ARIASection. activeBusinessId presente → query param/body client_id;
// ausente → legacy (sin client_id · backend cae a resolve_role LIMIT 1 / borra todo el user).

export function ariaHistoryQuery(activeBusinessId: string | null): string {
  return activeBusinessId ? `?client_id=${encodeURIComponent(activeBusinessId)}` : "";
}

export function ariaMessageBody(content: string, activeBusinessId: string | null): Record<string, unknown> {
  return { content, ...(activeBusinessId ? { client_id: activeBusinessId } : {}) };
}

export function ariaHistoryKey(activeBusinessId: string | null): (string | null)[] {
  return ["aria_history", activeBusinessId];
}
