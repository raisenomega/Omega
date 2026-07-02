import { Bell, Check } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { useNotifications } from "@/hooks/useNotifications";
import { Button } from "@/components/ui/button";

// Notificaciones REALES (tabla notifications · pieza 3) arriba del feed derivado del Card
// "Notificaciones". Solo muestra las no leídas · botón marcar-leída (PATCH guardado). Si no hay
// no-leídas → null (no ocupa espacio · el feed derivado sigue igual).
export function NotificationsBlock() {
  const { notifications, markRead } = useNotifications();
  const unread = notifications.filter((n) => !n.is_read);
  if (unread.length === 0) return null;

  return (
    <div className="space-y-2">
      {unread.map((n) => (
        <div key={n.id} className="flex items-start gap-3 rounded-lg border border-primary/30 bg-primary/5 p-3">
          <Bell className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium">{n.title}</p>
            {n.body && <p className="text-xs text-muted-foreground">{n.body}</p>}
            <span className="text-[10px] text-muted-foreground">
              {formatDistanceToNow(new Date(n.created_at), { addSuffix: true, locale: es })}
            </span>
          </div>
          <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0" title="Marcar leída" onClick={() => markRead.mutate(n.id)}>
            <Check className="h-3.5 w-3.5" />
          </Button>
        </div>
      ))}
    </div>
  );
}
