import { cn } from "@/lib/utils";
import { INTELLIGENCE_CHIPS, type ChipId } from "./_chips";

interface IntelligenceChipsProps {
  active: ChipId;
  onSelect: (id: ChipId) => void;
}

export function IntelligenceChips({ active, onSelect }: IntelligenceChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {INTELLIGENCE_CHIPS.map((chip) => (
        <button
          key={chip.id}
          type="button"
          onClick={() => onSelect(chip.id)}
          aria-pressed={active === chip.id}
          className={cn(
            "rounded-full px-4 py-1.5 text-sm border transition-colors",
            active === chip.id
              ? "border-amber-500 bg-amber-500/10 text-foreground"
              : "border-border/40 bg-transparent text-muted-foreground hover:border-amber-500/50",
          )}
        >
          {chip.label}
        </button>
      ))}
    </div>
  );
}
