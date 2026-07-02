import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";

// Select inline con trigger = Badge de color (réplica exacta del molde para Estado y Temperatura
// en la tabla). Cambiar el valor dispara onChange (→ PATCH guardado).
interface Props {
  value: string | null;
  options: string[];
  labels: Record<string, string>;
  colors: Record<string, string>;
  onChange: (v: string) => void;
}

export function InlineBadgeSelect({ value, options, labels, colors, onChange }: Props) {
  const v = value ?? "";
  return (
    <Select value={v || undefined} onValueChange={onChange}>
      <SelectTrigger className="h-7 w-[120px] border-0 p-0 text-xs">
        <Badge variant="outline" className={colors[v] ?? "text-muted-foreground"}>
          {labels[v] ?? "—"}
        </Badge>
      </SelectTrigger>
      <SelectContent>
        {options.map((o) => (
          <SelectItem key={o} value={o}>{labels[o] ?? o}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
