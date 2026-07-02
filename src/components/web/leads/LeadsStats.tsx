import { Card, CardContent } from "@/components/ui/card";
import type { Lead } from "@/hooks/useAdminLeads";
import { STATUS_LABELS } from "./lead-constants";

// 4 tarjetas de conteo por status (D3 · new/contacted/qualified/converted · réplica del molde).
const CARDS = ["new", "contacted", "qualified", "converted"];

export function LeadsStats({ leads }: { leads: Lead[] }) {
  return (
    <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
      {CARDS.map((s) => (
        <Card key={s} className="border-border">
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-foreground">{leads.filter((l) => l.status === s).length}</p>
            <p className="text-xs text-muted-foreground">{STATUS_LABELS[s]}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
