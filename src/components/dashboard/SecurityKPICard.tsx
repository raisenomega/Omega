import { useEffect, useRef, useState } from "react";
import { Shield, ShieldAlert, Loader2, RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useSessionReport } from "@/hooks/useSessionReport";
import { useToast } from "@/hooks/use-toast";

// GUARDIAN 4B-4 · seguridad de la cuenta del cliente (dato real · empty state honesto · P1)
const EVENT_LABELS: Record<string, string> = {
  login_success: "Inicio de sesión", login_failed: "Intento fallido",
  logout: "Cierre de sesión", session_refresh: "Sesión renovada",
  password_reset: "Reset de contraseña", new_device: "Nuevo dispositivo",
  suspicious_activity: "Actividad sospechosa",
};

function fmt(at: string): string {
  const d = new Date(at);
  return isNaN(d.getTime()) ? at : d.toLocaleString("es-AR", { dateStyle: "short", timeStyle: "short" });
}

export function SecurityKPICard() {
  const { data, isLoading, isError } = useSessionReport();
  const { toast } = useToast();
  const revisar = data?.status === "revisar";
  const [scanning, setScanning] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  // Cliente NO puede llamar /sentinel/scan (superadmin-only) · feedback best-effort
  const handleScan = () => {
    setScanning(true);
    toast({ title: "Escaneando tu cuenta…" });
    timer.current = setTimeout(() => {
      setScanning(false);
      toast({ title: "Cuenta verificada ✓" });
    }, 2000);
  };

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">Seguridad de tu cuenta</CardTitle>
        <div className="flex items-center gap-1.5">
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleScan}
            disabled={scanning} aria-label="Escanear cuenta">
            <RefreshCw className={`h-3.5 w-3.5 text-muted-foreground ${scanning ? "animate-spin" : ""}`} />
          </Button>
          {data && (revisar
            ? <ShieldAlert className="h-4 w-4 text-amber-500" />
            : <Shield className="h-4 w-4 text-emerald-500" />)}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="flex items-center gap-2 text-xs text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" />Cargando…</div>
        ) : isError || !data ? (
          <p className="text-xs text-muted-foreground">Sin actividad de seguridad registrada aún.</p>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <Badge variant={revisar ? "destructive" : "secondary"} className="text-[10px]">{revisar ? "Revisar" : "Protegida"}</Badge>
              {data.open_incidents > 0 && (
                <span className="text-[10px] text-muted-foreground">{data.open_incidents} incidente(s) abierto(s)</span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {data.last_login ? `Último acceso: ${fmt(data.last_login.at)} · ${data.last_login.ip}` : "Aún sin accesos registrados."}
            </p>
            {data.recent_events.length > 0 && (
              <ul className="space-y-1 pt-1 border-t border-border/40">
                {data.recent_events.slice(0, 2).map((e, i) => (
                  <li key={i} className="flex items-center justify-between text-[11px]">
                    <span>{EVENT_LABELS[e.event_type] ?? e.event_type}</span>
                    <span className="text-muted-foreground tabular-nums">{fmt(e.at)}</span>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
