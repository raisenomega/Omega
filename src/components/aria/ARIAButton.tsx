import { useARIA } from "@/contexts/ARIAContext";
import { useARIAChat } from "@/hooks/useARIAChat";

// ARIAButton · global en AppHeader · siempre visible.
// Fondo azul · CTA destacado · dot pulsante blanco indicador activo.
// FIX 3: nivel ARIA NO se elige aquí · sube automático con plan o ARIA Premium.
// Cero dropdowns/selectores/cascades (regla spec §6).
export function ARIAButton() {
  const { openARIA } = useARIA();
  const { ariaLevel } = useARIAChat();

  return (
    <button
      type="button"
      onClick={openARIA}
      aria-label={`Abrir ARIA ${ariaLevel}.0`}
      className="relative inline-flex items-center h-9 px-3 rounded-md bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
    >
      <span>ARIA</span>
      <sup className="text-[10px] opacity-70 ml-1 tabular-nums">{ariaLevel}.0</sup>
      <span
        className="absolute top-1 right-1 w-2 h-2 rounded-full bg-white animate-pulse"
        aria-hidden
      />
    </button>
  );
}
