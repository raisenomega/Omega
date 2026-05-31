import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

interface NewBusinessIntroDialogProps {
  isOpen: boolean;
  onAccept: () => void;
  onCancel: () => void;
}

// Diálogo educativo cálido que precede al wizard de 10 secciones (solo en creación · no en editar).
// Checkbox obligatorio: "Comenzar" se habilita solo al aceptar. Cierre por ESC/click-fuera/X → cancela.
// Se muestra SIEMPRE (sin "no mostrar de nuevo") · accepted se resetea cada vez que se abre.
export function NewBusinessIntroDialog({ isOpen, onAccept, onCancel }: NewBusinessIntroDialogProps) {
  const [accepted, setAccepted] = useState(false);
  useEffect(() => { if (isOpen) setAccepted(false); }, [isOpen]);

  return (
    <Dialog open={isOpen} onOpenChange={(o) => { if (!o) onCancel(); }}>
      <DialogContent className="max-w-lg">
        <DialogTitle className="text-lg font-display font-bold tracking-tight">🌱 Antes de empezar</DialogTitle>
        <div className="space-y-5 text-sm">
          <div className="space-y-3 text-muted-foreground">
            <p>Vas a crear un nuevo negocio en OmegaRaisen, y ARIA va a aprender de él para asistirte de verdad.</p>
            <p>Las próximas 10 secciones le dan a ARIA todo lo que necesita saber:</p>
            <ul className="space-y-1 pl-1">
              <li>• Tu marca y voz</li>
              <li>• Tu audiencia ideal</li>
              <li>• Tus productos o servicios</li>
              <li>• Tus objetivos y métricas</li>
              <li>• Tus redes sociales</li>
            </ul>
          </div>
          <div className="space-y-3 rounded-lg border border-border/60 bg-muted/30 p-4">
            <p className="font-medium text-foreground">💡 Llená el 100% para resultados reales</p>
            <p className="text-muted-foreground">Cada sección que dejes incompleta es contexto que ARIA no tiene. Y sin contexto, ARIA solo puede generar contenido genérico, no contenido tuyo.</p>
            <p className="text-muted-foreground">Llenarlo al 100% no es un trámite — es lo que hace la diferencia entre un asistente que te suena parecido y uno que suena exactamente como vos.</p>
            <p className="text-muted-foreground">Cuanto más detalle, mejor te entiende.</p>
            <p className="text-xs text-muted-foreground/80">⏱ ~10 minutos · tomate el tiempo que necesites</p>
          </div>
          <label className="flex items-start gap-3 cursor-pointer">
            <Checkbox checked={accepted} onCheckedChange={(v) => setAccepted(v === true)} className="mt-0.5" />
            <span className="text-muted-foreground leading-snug">Entiendo que llenar todas las secciones con detalle es lo que define la calidad del trabajo de ARIA con mi negocio</span>
          </label>
        </div>
        <div className="flex justify-end">
          <Button className="gradient-primary" disabled={!accepted} onClick={onAccept}>Comenzar</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
