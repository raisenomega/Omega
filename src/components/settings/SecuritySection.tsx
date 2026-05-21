import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, LogOut, Mail, Smartphone } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

function parseDevice(ua: string): string {
  if (!ua) return "—";
  const browser = ua.includes("Chrome") ? "Chrome" : ua.includes("Firefox") ? "Firefox" : ua.includes("Safari") ? "Safari" : "Navegador";
  const os = ua.includes("Windows") ? "Windows" : ua.includes("Mac") ? "macOS" : ua.includes("Linux") ? "Linux" : ua.includes("iPhone") ? "iPhone" : ua.includes("Android") ? "Android" : "Sistema";
  return `${browser} en ${os}`;
}

export function SecuritySection() {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [sending, setSending] = useState(false);
  const email = user?.email ?? "";
  const device = typeof window !== "undefined" ? parseDevice(window.navigator.userAgent) : "—";

  const handleReset = async () => {
    setSending(true);
    const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo: `${window.location.origin}/auth` });
    setSending(false);
    if (error) { toast({ title: "Error", description: error.message, variant: "destructive" }); return; }
    toast({ title: "Email enviado", description: `Revisa ${email} para restablecer tu contraseña.` });
  };

  const handleLogout = async () => { await signOut(); navigate("/auth"); };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Mail className="h-4 w-4" />Email</CardTitle></CardHeader>
        <CardContent className="flex items-center gap-2 text-sm">
          <span className="flex-1 truncate">{email}</span>
          <Badge variant="secondary" className="h-5 text-[10px]">Verificado</Badge>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Lock className="h-4 w-4" />Contraseña</CardTitle></CardHeader>
        <CardContent>
          <Button size="sm" variant="outline" onClick={handleReset} disabled={sending || !email}>
            {sending ? "Enviando…" : "Cambiar contraseña"}
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Smartphone className="h-4 w-4" />Sesión activa</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p className="text-xs text-muted-foreground">{device}</p>
          <Button size="sm" variant="outline" onClick={handleLogout} className="gap-1 text-destructive">
            <LogOut className="h-3.5 w-3.5" />Cerrar sesión
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
