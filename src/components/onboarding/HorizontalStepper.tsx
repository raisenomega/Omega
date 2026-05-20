import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { SECTIONS } from "./sections/registry";

interface HorizontalStepperProps {
  activeIndex: number;
  completedIndices: Set<number>;
  onJump: (index: number) => void;
}

// Navegación libre (FIX 3): cualquier dot es clickable · sin gating.
// El único gate vive en el botón "Crear Cliente" (WizardFooter).
export function HorizontalStepper({
  activeIndex, completedIndices, onJump,
}: HorizontalStepperProps) {
  return (
    <div className="border-b border-border bg-background/95 px-4 py-3 overflow-x-auto">
      <ol className="flex items-start min-w-max md:min-w-0 md:w-full">
        {SECTIONS.map((s, i) => {
          const isActive = i === activeIndex;
          const isDone = completedIndices.has(i);
          return (
            <li key={s.id} className="flex-1 flex flex-col items-center min-w-[64px] md:min-w-0">
              <div className="flex items-center w-full">
                {i > 0 && (
                  <div className={cn(
                    "h-px flex-1 mx-1",
                    completedIndices.has(i - 1) ? "bg-emerald-500" : "bg-border",
                  )} />
                )}
                <button
                  type="button"
                  onClick={() => onJump(i)}
                  className={cn(
                    "h-7 w-7 shrink-0 rounded-full flex items-center justify-center text-xs font-semibold transition cursor-pointer",
                    isActive && "bg-primary text-primary-foreground ring-2 ring-primary/30 ring-offset-2 ring-offset-background",
                    !isActive && isDone && "bg-emerald-500 text-white hover:bg-emerald-600",
                    !isActive && !isDone && "bg-muted text-muted-foreground hover:bg-muted/80",
                  )}
                  aria-current={isActive ? "step" : undefined}
                  aria-label={`Ir a sección ${i + 1}: ${s.title}`}
                >
                  {isDone && !isActive ? <Check className="h-3.5 w-3.5" /> : i + 1}
                </button>
                {i < SECTIONS.length - 1 && (
                  <div className={cn(
                    "h-px flex-1 mx-1",
                    isDone ? "bg-emerald-500" : "bg-border",
                  )} />
                )}
              </div>
              <span className={cn(
                "text-[10px] mt-1.5 truncate max-w-[80px] text-center leading-tight",
                isActive ? "text-foreground font-medium" : "text-muted-foreground",
              )}>
                {s.title}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
