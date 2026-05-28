// DEBT-099 · pantalla bienvenida pre-wizard · onStart toggle a la vista del wizard.
import { Button } from "@/components/ui/button";
import { RaisenCircleLogo } from "@/components/brand/RaisenCircleLogo";
import { Sparkles, Calendar, BarChart3 } from "lucide-react";

interface Props { onStart: () => void }

export default function OnboardingWelcome({ onStart }: Props) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="max-w-md text-center space-y-6">
        <div className="flex justify-center"><RaisenCircleLogo size={56} /></div>
        <h1 className="text-2xl font-semibold">Bienvenido a OMEGA</h1>
        <p className="text-sm text-muted-foreground">
          En 5 minutos vamos a configurar tu workspace: tu negocio, tu voz de marca,
          tus objetivos. Después ARIA y los agentes saben exactamente cómo trabajar para vos.
        </p>
        <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
          <div className="flex flex-col items-center gap-1"><Sparkles className="h-5 w-5" /><span>Contenido</span></div>
          <div className="flex flex-col items-center gap-1"><Calendar className="h-5 w-5" /><span>Calendario</span></div>
          <div className="flex flex-col items-center gap-1"><BarChart3 className="h-5 w-5" /><span>Analytics</span></div>
        </div>
        <Button onClick={onStart} size="lg" className="w-full gradient-primary">Empecemos</Button>
        <p className="text-[10px] text-muted-foreground">Plan Adopción · 7 días gratis · sin tarjeta</p>
      </div>
    </div>
  );
}
