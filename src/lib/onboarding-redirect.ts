// DEBT-099 · self-service onboarding · pura · sin imports de React/Supabase/Router.
// Extraída del hook useAutoRedirectFirstTime para testabilidad sin mocks ni jsdom.
// Placeholder = auto-trigger 00006 (name='Mi negocio' + industry NULL). El user lo
// "rompe" con CUALQUIER cambio en uno de los dos campos.

export const ONBOARDING_PATH = "/onboarding";

export interface ClientPlaceholderCheck { name: string; industry: string | null }

export interface RedirectArgs {
  client: ClientPlaceholderCheck | null;
  isOwner: boolean;       // dueño de algún reseller · bypass
  isSuperadmin: boolean;  // super_owner · bypass
  loading: boolean;
  currentPath: string;
}

export function shouldRedirectToOnboarding(args: RedirectArgs): boolean {
  if (args.loading) return false;
  if (args.currentPath === ONBOARDING_PATH) return false;
  if (args.isOwner || args.isSuperadmin) return false;  // bypass reseller/super_owner
  if (!args.client) return false;
  return args.client.name === "Mi negocio" && !args.client.industry;
}
