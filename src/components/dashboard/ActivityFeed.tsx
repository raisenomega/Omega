import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, History } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { getNetworkIcon } from "@/lib/network-icons";
import { Button } from "@/components/ui/button";
import { ActivityHistoryDialog, type ActivityItem } from "./ActivityHistoryDialog";

interface Client {
  id: string;
  name: string;
  business_type: string | null;
  status: string;
  created_at: string;
}

interface SocialAccount {
  id: string;
  platform: string;
  account_name: string;
  status: string;
  created_at: string;
  clients?: { name: string } | null;
}

interface ActivityFeedProps {
  recentClients: Client[];
  recentAccounts: SocialAccount[];
}

export function ActivityFeed({ recentClients, recentAccounts }: ActivityFeedProps) {
  const [historyOpen, setHistoryOpen] = useState(false);

  const all: ActivityItem[] = [
    ...recentClients.map((c) => ({
      id: c.id,
      type: "client" as const,
      title: `Nuevo cliente: ${c.name}`,
      subtitle: c.business_type || "Sin industria",
      time: c.created_at,
      icon: Users,
    })),
    ...recentAccounts.map((a) => ({
      id: a.id,
      type: "account" as const,
      title: a.account_name,
      subtitle: `${a.platform} · ${a.status === "active" ? "Activa" : a.status === "expired" ? "Expirada" : "Desconectada"}`,
      time: a.created_at,
      icon: getNetworkIcon(a.platform).icon,
      platform: a.platform,
    })),
  ].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());

  const top3 = all.slice(0, 3);

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg">Actividad Reciente</CardTitle>
      </CardHeader>
      <CardContent>
        {top3.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <Users className="h-10 w-10 mb-2 opacity-30" />
            <p className="text-sm">Sin actividad reciente</p>
            <p className="text-xs mt-1">Agrega clientes y cuentas para empezar</p>
          </div>
        ) : (
          <>
            <div className="space-y-3">
              {top3.map((activity) => (
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
            <Button
              variant="ghost"
              size="sm"
              className="mt-3 w-full"
              onClick={() => setHistoryOpen(true)}
            >
              <History className="h-4 w-4" />
              Ver historial
            </Button>
          </>
        )}
      </CardContent>
      <ActivityHistoryDialog activities={all} open={historyOpen} onOpenChange={setHistoryOpen} />
    </Card>
  );
}
