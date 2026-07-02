import { Search, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { STATUSES, STATUS_LABELS, TEMPERATURES, TEMP_LABELS } from "./lead-constants";

export interface FilterState {
  search: string;
  status: string;
  temp: string;
  audience: string;
  source: string;
}

interface Props {
  value: FilterState;
  set: (patch: Partial<FilterState>) => void;
  sources: string[]; // fuentes distintas presentes (D7 · embudos reales)
}

// Buscador (nombre/email/empresa) + 4 selects. "all"→"" (radix no admite value vacío).
export function LeadsFilters({ value, set, sources }: Props) {
  const sel = (v: string, on: (x: string) => void, ph: string, opts: [string, string][]) => (
    <Select value={v || "all"} onValueChange={(x) => on(x === "all" ? "" : x)}>
      <SelectTrigger className="w-[150px]"><Filter size={14} className="mr-1 shrink-0" /><SelectValue placeholder={ph} /></SelectTrigger>
      <SelectContent>
        <SelectItem value="all">{ph}</SelectItem>
        {opts.map(([o, l]) => <SelectItem key={o} value={o}>{l}</SelectItem>)}
      </SelectContent>
    </Select>
  );
  return (
    <div className="mb-6 flex flex-wrap gap-3">
      <div className="relative min-w-[200px] flex-1">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Buscar por nombre, email o empresa..." value={value.search} onChange={(e) => set({ search: e.target.value })} className="pl-9" />
      </div>
      {sel(value.status, (x) => set({ status: x }), "Todos (estado)", STATUSES.map((s) => [s, STATUS_LABELS[s]]))}
      {sel(value.temp, (x) => set({ temp: x }), "Todos (temp)", TEMPERATURES.map((t) => [t, TEMP_LABELS[t]]))}
      {sel(value.audience, (x) => set({ audience: x }), "Toda audiencia", [["pyme", "PYME"], ["reseller", "Agencia"]])}
      {sel(value.source, (x) => set({ source: x }), "Toda fuente", sources.map((s) => [s, s]))}
    </div>
  );
}
