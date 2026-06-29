import { cn } from "@/lib/utils";

export interface ChipItem {
  id: string;
  label: string;
}

interface FilterChipsProps {
  items: ChipItem[];
  active: string;
  onSelect: (id: string) => void;
}

// Chip genérico oficial de la app (pill seleccionable · color de marca PRIMARY).
// 1er consumidor: el selector Mes/Semana/Día del Calendario. Analytics/Inteligencia/ARIA
// convergen a este componente después (hoy cada una tiene su variante · ver SOT). Genérico
// de verdad: solo items + active + onSelect · cero acoplamiento a ningún dominio.
export function FilterChips({ items, active, onSelect }: FilterChipsProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {items.map((it) => (
        <button
          key={it.id}
          type="button"
          onClick={() => onSelect(it.id)}
          className={cn(
            "rounded-full border px-3 py-1.5 text-sm transition-colors",
            active === it.id
              ? "border-primary bg-primary/10 text-foreground"
              : "border-border/40 text-muted-foreground hover:border-primary/50",
          )}
        >
          {it.label}
        </button>
      ))}
    </div>
  );
}
