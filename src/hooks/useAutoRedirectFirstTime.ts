// DEBT-099-v2 · wizard opcional · no-op preservado.
// El redirect forzado se eliminó por decisión de producto (dashboard-first).
// El hook se conserva como no-op para no romper el caller ProtectedRoute.tsx.
// El nudge en /dashboard ahora invita al wizard sin obligar.
export function useAutoRedirectFirstTime(): void {
  // intencionalmente vacío · ver lib/onboarding-redirect.ts
}
