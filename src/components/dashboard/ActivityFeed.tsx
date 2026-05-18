import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Wifi } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";

interface Client {
  id: string;
  name: string;
  company: string | null;
  active: boolean;
  created_at: string;
}

interface SocialAccount {
  id: string;
  platform: string;
  account_name: string;
  connected: boolean;
  created_at: string;
  clients?: { name: string } | null;
}

interface ActivityFeedProps {
  recentClients: Client[];
  recentAccounts: SocialAccount[];
}

const PLATFORM_EMOJI: Record<string, string> = {
  instagram: "📸",
  facebook: "📘",
  tiktok: "🎵",
  twitter: "🐦",
  linkedin: "💼",
  youtube: "🎬",
};

export function ActivityFeed({ recentClients, recentAccounts }: ActivityFeedProps) {
  const allActivities = [
    ...recentClients.map((c) => ({
      id: c.id,
      type: "client" as const,
      title: `Nuevo cliente: ${c.name}`,
      subtitle: c.company || "Sin empresa",
      time: c.created_at,
      icon: Users,
    })),
    ...recentAccounts.map((a) => ({
      id: a.id,
      type: "account" as const,
      title: `${PLATFORM_EMOJI[a.platform] || "🌐"} ${a.account_name}`,
      subtitle: `${a.platform} • ${a.connected ? "Conectada" : "Pendiente"}`,
      time: a.created_at,
      icon: Wifi,
    })),
  ].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()).slice(0, 8);

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg">Actividad Reciente</CardTitle>
      </CardHeader>
      <CardContent>
        {allActivities.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <Users className="h-10 w-10 mb-2 opacity-30" />
            <p className="text-sm">Sin actividad reciente</p>
            <p className="text-xs mt-1">Agrega clientes y cuentas para empezar</p>
          </div>
        ) : (
          <div className="space-y-3">
            {allActivities.map((activity) => (
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
      </CardContent>
    </Card>
  );
}
