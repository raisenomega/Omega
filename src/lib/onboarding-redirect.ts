// DEBT-099-v2 · wizard opcional · dashboard-first.
// El redirect forzado al wizard quedó eliminado por decisión de producto:
// el cliente entra directo al /dashboard y el wizard se abre por acción
// suya (vía NudgeFirstClient). isPlaceholderClient sigue exportada porque
// el nudge la usa para decidir si mostrarse.

export const ONBOARDING_PATH = "/onboarding";

export interface ClientPlaceholderCheck { name: string; industry: string | null }

export interface RedirectArgs {
  client: ClientPlaceholderCheck | null;
  isOwner: boolean;
  isSuperadmin: boolean;
  loading: boolean;
  currentPath: string;
}

export function shouldRedirectToOnboarding(_args: RedirectArgs): boolean {
  return false;
}

export function isPlaceholderClient(client: ClientPlaceholderCheck | null): boolean {
  if (!client) return false;
  return client.name === "Mi negocio" && !client.industry;
}
