// DEBT-099-v2 · invitación suave al wizard cuando el cliente aún no rompió el
// placeholder. Se auto-oculta cuando el user agrega cliente real. Fondo verde
// que respira (animate-breathe-green) · motion-reduce:animate-none lo deja
// estático si el sistema pide reduced-motion · accesibilidad cubierta.
import { useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useHasPlaceholderClient } from "@/hooks/useHasPlaceholderClient";
import { ONBOARDING_PATH } from "@/lib/onboarding-redirect";

export function NudgeFirstClient() {
  const navigate = useNavigate();
  const { isPlaceholder, loading } = useHasPlaceholderClient();

  if (loading || !isPlaceholder) return null;

  return (
    <button
      type="button"
      onClick={() => navigate(ONBOARDING_PATH)}
      className="group w-full rounded-xl border border-emerald-500/40 bg-emerald-500/15 px-5 py-4 text-left animate-breathe-green motion-reduce:animate-none transition-colors hover:bg-emerald-500/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
      aria-label="Agregá tu primer cliente · abre el asistente"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-500/30">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white">Agregá tu primer cliente</p>
          <p className="text-xs text-white/80">Contale a ARIA de tu negocio y empezá a crear</p>
        </div>
      </div>
    </button>
  );
}
