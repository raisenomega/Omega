import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ARIA_LEVELS } from "@/lib/aria-levels";

// Chips horizontales de los 4 niveles ARIA · nivel actual highlighted · tooltip hover por nivel.
// Vive en el Tab Agente (columna Nivel ARIA), no en el modal. Copy de tooltip local (textos
// comerciales con precio/disponibilidad específicos de esta vista · el label viene de ARIA_LEVELS).
const ARIA_CHIP_TOOLTIP: Record<number, string> = {
  1: "Conversacional básico · onboarding y respuestas FAQ. Incluido en tu plan.",
  2: "Sugerencias de contenido + análisis simple de tu marca. +$12/mes",
  3: "NBA engine · predice tu mejor próxima acción + auto-publicación con aprobación. Disponible desde ARIA 2.0",
  4: "Contexto extendido · acciones autónomas con guardrails · análisis profundo de audiencia. Disponible desde ARIA 3.0",
};

export function AriaLevelChips({ currentLevel }: { currentLevel: number }) {
  return (
    <TooltipProvider>
      <div className="flex flex-wrap gap-1.5">
        {[1, 2, 3, 4].map((lvl) => {
          const isCurrent = lvl === currentLevel;
          const label = isCurrent ? ARIA_LEVELS[lvl].label : `ARIA ${lvl}.0`;
          return (
            <Tooltip key={lvl}>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className={`rounded-full px-2 py-1 text-[10px] font-medium transition-colors ${
                    isCurrent ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                  }`}
                >
                  {label}
                </button>
              </TooltipTrigger>
              <TooltipContent side="top" className="max-w-[16rem] text-xs">
                {ARIA_CHIP_TOOLTIP[lvl]}
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </TooltipProvider>
  );
}
