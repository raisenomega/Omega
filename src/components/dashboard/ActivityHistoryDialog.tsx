import { useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PLATFORM_LABELS } from "@/lib/network-icons";

export interface ActivityItem {
  id: string;
  type: "client" | "account";
  title: string;
  subtitle: string;
  time: string;
  icon: LucideIcon;
  platform?: string;
}

interface ActivityHistoryDialogProps {
  activities: ActivityItem[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const CLIENTS_FILTER = "__clients__";

export function ActivityHistoryDialog({ activities, open, onOpenChange }: ActivityHistoryDialogProps) {
  const [filter, setFilter] = useState<string>("all");

  const platforms = useMemo(
    () => Array.from(new Set(activities.filter((a) => a.platform).map((a) => a.platform as string))),
    [activities],
  );
  const hasClients = useMemo(() => activities.some((a) => a.type === "client"), [activities]);

  const filtered = useMemo(() => {
    const list = activities.filter((a) =>
      filter === "all" ? true : filter === CLIENTS_FILTER ? a.type === "client" : a.platform === filter,
    );
    return [...list].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());
  }, [activities, filter]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg border-border/50 bg-card">
        <DialogHeader>
          <DialogTitle>Historial de actividad</DialogTitle>
        </DialogHeader>

        <div className="flex flex-wrap gap-2">
          {[
            { value: "all", label: "Todo" },
            ...platforms.map((p) => ({ value: p, label: PLATFORM_LABELS[p] ?? p })),
            ...(hasClients ? [{ value: CLIENTS_FILTER, label: "Clientes" }] : []),
          ].map((chip) => (
            <Button
              key={chip.value}
              variant={filter === chip.value ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(chip.value)}
            >
              {chip.label}
            </Button>
          ))}
        </div>

        <ScrollArea className="max-h-[50vh] pr-3">
          {filtered.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">Sin actividad para este filtro</p>
          ) : (
            <div className="space-y-3">
              {filtered.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center gap-3 rounded-lg border border-border/30 bg-muted/30 p-3 transition-colors hover:bg-muted/50"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                    <activity.icon className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{activity.title}</p>
                    <p className="text-xs text-muted-foreground">{activity.subtitle}</p>
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {formatDistanceToNow(new Date(activity.time), { addSuffix: true, locale: es })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
