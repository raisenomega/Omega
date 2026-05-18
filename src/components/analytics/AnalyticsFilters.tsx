import { useState } from "react";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface AnalyticsFiltersProps {
  clients: { id: string; name: string }[];
  selectedClient: string;
  onClientChange: (v: string) => void;
  dateRange: { from: Date | undefined; to: Date | undefined };
  onDateRangeChange: (range: { from: Date | undefined; to: Date | undefined }) => void;
}

export function AnalyticsFilters({
  clients,
  selectedClient,
  onClientChange,
  dateRange,
  onDateRangeChange,
}: AnalyticsFiltersProps) {
  return (
    <div className="flex flex-wrap gap-3">
      <Select value={selectedClient} onValueChange={onClientChange}>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Todos los clientes" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Todos los clientes</SelectItem>
          {clients.map((c) => (
            <SelectItem key={c.id} value={c.id}>
              {c.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              "w-[240px] justify-start text-left font-normal",
              !dateRange.from && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {dateRange.from ? (
              dateRange.to ? (
                <>
                  {format(dateRange.from, "dd MMM", { locale: es })} –{" "}
                  {format(dateRange.to, "dd MMM", { locale: es })}
                </>
              ) : (
                format(dateRange.from, "dd MMM yyyy", { locale: es })
              )
            ) : (
              "Rango de fechas"
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="range"
            selected={dateRange}
            onSelect={(range) =>
              onDateRangeChange({
                from: range?.from,
                to: range?.to,
              })
            }
            numberOfMonths={2}
            className="p-3 pointer-events-auto"
          />
        </PopoverContent>
      </Popover>

      {(selectedClient !== "all" || dateRange.from) && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            onClientChange("all");
            onDateRangeChange({ from: undefined, to: undefined });
          }}
        >
          Limpiar filtros
        </Button>
      )}
    </div>
  );
}
