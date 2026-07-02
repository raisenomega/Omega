import { lazy } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { RaisenLogo } from "@/components/brand/RaisenLogo";

// Fase 1 · landing pública · reemplaza el redirect incondicional de "/" (antes App.tsx:71).
// loading → MISMO fallback que ProtectedRoute (NUNCA landing mientras carga · evita flash a
// logueados) · session → /dashboard (byte-idéntico al comportamiento previo) · anónimo → landing lazy.
const LandingPage = lazy(() => import("@/pages/LandingPage"));

export function RootRoute() {
  const { session, loading } = useAuth();

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

  if (session) {
    return <Navigate to="/dashboard" replace />;
  }

  return <LandingPage />;
}
