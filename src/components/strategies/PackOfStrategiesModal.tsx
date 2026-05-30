import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

// Pack de Estrategias · upsell coming-soon (DEBT-STRATEGY-QUOTAS-PACKS · aún no habilitado).
// Copy seguro P1: afirma que la MARCA del cliente madura con uso consistente (cierto por la
// naturaleza del marketing de contenidos), NO que el sistema aprende (eso es DEBT-ARIA-LEARNING-REAL,
// sin verificar). Sin CTAs falsos (no "te avisamos"/email): no hay sistema de notificaciones. Solo cierre.
export function PackOfStrategiesModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4" /> Pack de Estrategias
          </DialogTitle>
          <DialogDescription className="text-xs">Próximamente — coming soon</DialogDescription>
        </DialogHeader>
        <div className="space-y-3 text-sm text-muted-foreground">
          <p>Por ahora, ARIA te entrega estrategias automáticamente según tu plan. Cada estrategia que uses afina tu voz de marca y la hace madurar — más reconocible, más tuya.</p>
          <p>Cuando habilitemos los packs, podrás solicitar estrategias adicionales en los momentos que más lo necesites — campañas de temporada, lanzamientos, o aceleraciones puntuales.</p>
          <p className="font-medium text-foreground">Usa las que ya recibes. Cada una cuenta.</p>
        </div>
        <div className="flex justify-end pt-2">
          <Button variant="outline" onClick={onClose}>Entendido</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
