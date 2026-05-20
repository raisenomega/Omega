import { cn } from "@/lib/utils";

interface PillGroupProps {
  options: readonly string[];
  labels?: Record<string, string>;
  value: string | string[];
  onChange: (v: string | string[]) => void;
  multi?: boolean;
  cols?: 3 | 4 | 5 | 6 | 7;
}

const COLS_MAP: Record<3 | 4 | 5 | 6 | 7, string> = {
  3: "grid-cols-3",
  4: "grid-cols-4",
  5: "grid-cols-5",
  6: "grid-cols-6",
  7: "grid-cols-7",
};

function isSelected(value: string | string[], option: string): boolean {
  return Array.isArray(value) ? value.includes(option) : value === option;
}

export function PillGroup({
  options, labels, value, onChange, multi = false, cols = 4,
}: PillGroupProps) {
  const handleClick = (option: string) => {
    if (multi) {
      const arr = Array.isArray(value) ? value : [];
      onChange(arr.includes(option) ? arr.filter((x) => x !== option) : [...arr, option]);
      return;
    }
    onChange(value === option ? "" : option);
  };

  return (
    <div className={cn("grid gap-1.5", COLS_MAP[cols])}>
      {options.map((opt) => {
        const active = isSelected(value, opt);
        return (
          <button
            key={opt}
            type="button"
            onClick={() => handleClick(opt)}
            className={cn(
              "rounded-full px-3 py-1 text-xs border transition cursor-pointer",
              active
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-muted/40 text-muted-foreground border-border/50 hover:bg-muted/60",
            )}
            aria-pressed={active}
          >
            {labels?.[opt] ?? opt}
          </button>
        );
      })}
    </div>
  );
}
