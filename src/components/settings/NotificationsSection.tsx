import { useEffect, useState } from "react";
import { FileText, Bell, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useClientPlanStatus } from "@/hooks/useClientPlanStatus";

interface NotifPrefs { failures: boolean; renewal: boolean; weekly_aria: boolean }
const STORAGE_KEY = "notification_prefs";
const DEFAULTS: NotifPrefs = { failures: true, renewal: true, weekly_aria: false };

function loadPrefs(): NotifPrefs {
  if (typeof window === "undefined") return DEFAULTS;
  try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") }; } catch { return DEFAULTS; }
}

interface NotificationsSectionProps { clientId: string | null }

export function NotificationsSection({ clientId }: NotificationsSectionProps) {
  const plan = useClientPlanStatus(clientId ?? "");
  const isPro = plan.planCode === "pro" || plan.planCode === "enterprise";
  const [prefs, setPrefs] = useState<NotifPrefs>(loadPrefs);
  useEffect(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); }, [prefs]);
  const reportFreq = isPro ? "Semanal · cada lunes" : "Mensual · primer día del mes";

  const toggle = (k: keyof NotifPrefs) => setPrefs((p) => ({ ...p, [k]: !p[k] }));

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Bell className="h-4 w-4" />Preferencias</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <label className="flex items-center justify-between text-sm cursor-pointer">
            <span>Alertas de posts fallidos</span>
            <Switch checked={prefs.failures} onCheckedChange={() => toggle("failures")} />
          </label>
          <label className="flex items-center justify-between text-sm cursor-pointer">
            <span>Alertas de renovación próxima</span>
            <Switch checked={prefs.renewal} onCheckedChange={() => toggle("renewal")} />
          </label>
          <label className={`flex items-center justify-between text-sm ${isPro ? "cursor-pointer" : "opacity-50"}`}>
            <span>Resumen semanal ARIA {!isPro && <span className="text-[10px] text-muted-foreground">(solo plan Pro)</span>}</span>
            <Switch checked={prefs.weekly_aria && isPro} disabled={!isPro} onCheckedChange={() => toggle("weekly_aria")} />
          </label>
          <p className="text-[10px] text-muted-foreground pt-1">Preferencias guardadas en este dispositivo · se aplicarán al Bell cuando notifications esté disponible.</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><FileText className="h-4 w-4" />Reportes ARIA descargables</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p className="text-xs text-muted-foreground">Frecuencia: <span className="text-foreground font-medium">{reportFreq}</span></p>
          <Button size="sm" variant="outline" disabled className="gap-1" title="DEBT futura · Fase 2">
            <Download className="h-3.5 w-3.5" />Descargar último reporte
          </Button>
          <p className="text-[10px] text-muted-foreground">Incluye resumen de publicaciones, engagement y recomendaciones ARIA.</p>
        </CardContent>
      </Card>
    </div>
  );
}
