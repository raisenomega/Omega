// DEBT-099 · espera verificación email del user · polling cada 3s · timeout 60s.
// En la mayoría de configs Supabase, login requiere email confirmado → si el user
// llegó acá ya está confirmed. Este guard cubre la ventana edge entre signUp y
// confirmación si Supabase permite session sin verificar (config dependiente).
import { useEffect, useState } from "react";
import { Loader2, Mail } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";

const POLL_MS = 3000;
const TIMEOUT_MS = 60000;

interface Props { children: React.ReactNode }

export function EmailVerificationGuard({ children }: Props) {
  const { user } = useAuth();
  const [timedOut, setTimedOut] = useState(false);
  const confirmed = !!user?.email_confirmed_at;

  useEffect(() => {
    if (confirmed) return;
    const start = Date.now();
    const interval = setInterval(async () => {
      await supabase.auth.getUser();  // refresca session · onAuthStateChange propaga
      if (Date.now() - start > TIMEOUT_MS) {
        setTimedOut(true);
        clearInterval(interval);
      }
    }, POLL_MS);
    return () => clearInterval(interval);
  }, [confirmed]);

  if (confirmed) return <>{children}</>;
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <Mail className="h-10 w-10 text-muted-foreground mb-4" />
      <h2 className="text-lg font-semibold mb-2">Confirmá tu email</h2>
      <p className="text-sm text-muted-foreground max-w-sm mb-4">
        Te enviamos un link a <strong>{user?.email ?? "tu email"}</strong>. Hacé clic ahí para activar tu cuenta.
      </p>
      {timedOut
        ? <p className="text-xs text-muted-foreground">No detectamos la verificación · revisá spam o reintentá manualmente desde tu correo.</p>
        : <div className="flex items-center gap-2 text-xs text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" /> Esperando confirmación...</div>}
    </div>
  );
}
