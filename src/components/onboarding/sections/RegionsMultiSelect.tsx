import { Check, ChevronsUpDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { cn } from "@/lib/utils";
import { REGIONS, type Region } from "@/lib/client-constants";

interface RegionsMultiSelectProps {
  value: Region[];
  onChange: (next: Region[]) => void;
}

export function RegionsMultiSelect({ value, onChange }: RegionsMultiSelectProps) {
  const toggle = (r: Region) =>
    onChange(value.includes(r) ? value.filter((x) => x !== r) : [...value, r]);

  return (
    <>
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline" className="h-9 w-full justify-between font-normal">
            {value.length > 0 ? `${value.length} región(es) seleccionada(s)` : "Selecciona regiones"}
            <ChevronsUpDown className="h-4 w-4 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0">
          <Command>
            <CommandInput placeholder="Buscar región..." />
            <CommandList>
              <CommandEmpty>Sin resultados</CommandEmpty>
              <CommandGroup>
                {REGIONS.map((r) => (
                  <CommandItem key={r} onSelect={() => toggle(r)} className="cursor-pointer">
                    <Check className={cn("mr-2 h-4 w-4", value.includes(r) ? "opacity-100" : "opacity-0")} />
                    {r}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {value.map((r) => (
            <Badge key={r} variant="secondary" className="gap-1 pr-1">
              {r}
              <button type="button" onClick={() => toggle(r)} aria-label={`Remover ${r}`} className="hover:bg-background rounded p-0.5">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </>
  );
}
