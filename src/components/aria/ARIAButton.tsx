import { useARIA } from "@/contexts/ARIAContext";
import { useARIAChat } from "@/hooks/useARIAChat";

// ARIAButton · global en AppHeader · siempre visible.
// Fondo azul · borde flasheando verde↔blanco como CTA llamativa.
// FIX 3: cero dropdowns/selectores/cascades · nivel sube por plan o ARIA Premium.
// Texto: "ARIA" principal · "Modelo X.0" descriptivo (estilo subtitle de StatsCard).
export function ARIAButton() {
  const { openARIA } = useARIA();
  const { ariaLevel } = useARIAChat();

  return (
    <button
      type="button"
      onClick={openARIA}
      aria-label={`Abrir ARIA Modelo ${ariaLevel}.0`}
      className="relative inline-flex items-center gap-2 h-9 px-4 rounded-md bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium border-2 animate-border-flash transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
    >
      <span>ARIA</span>
      <span className="text-xs text-white/70 tabular-nums">Modelo {ariaLevel}.0</span>
      <span
        className="absolute top-1 right-1 w-2 h-2 rounded-full bg-white animate-pulse"
        aria-hidden
      />
    </button>
  );
}
