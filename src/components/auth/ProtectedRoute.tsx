import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { useAutoRedirectFirstTime } from "@/hooks/useAutoRedirectFirstTime";
import { RaisenLogo } from "@/components/brand/RaisenLogo";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { session, loading } = useAuth();
  // DEBT-099 · si el client del user es placeholder (auto-trigger 00006) y no es
  // reseller/super_owner → redirige a /onboarding. No corre en /onboarding mismo.
  useAutoRedirectFirstTime();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4 animate-pulse">
          <RaisenLogo size="xl" />
          <p className="text-sm text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/auth" replace />;
  }

  return <>{children}</>;
}
