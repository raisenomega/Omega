import { Minimize2, Calendar, Check, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import type { ModalState, BlockState } from "@/components/content/ResultCardV2";

interface Props {
  state: ModalState;
  block: BlockState;
  scheduledAt: string;
  setScheduledAt: (v: string) => void;
  onMinimize: () => void;
  onRestore: () => void;
  onClose: () => void;
  onConfirm: () => void;
}

const SLOTS = [
  { key: "caption" as const, icon: "📝", label: "Caption" },
  { key: "image" as const, icon: "🖼️", label: "Imagen" },
  { key: "hashtags" as const, icon: "#", label: "Hashtags" },
];

function Slot({ icon, label, filled, preview }: { icon: string; label: string; filled: boolean; preview?: string }) {
  return (
    <div className={`flex items-center gap-2 p-2 rounded-md border ${filled ? "border-emerald-300 bg-emerald-50 dark:bg-emerald-950/30" : "border-dashed border-muted opacity-60"}`}>
      <span className="text-lg">{icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium">{label}</p>
        {filled && preview && <p className="text-[10px] text-muted-foreground truncate">{preview}</p>}
      </div>
      {filled ? <Check className="h-4 w-4 text-emerald-600" /> : <Plus className="h-4 w-4 text-muted-foreground" />}
    </div>
  );
}

export function ScheduleModalV2({ state, block, scheduledAt, setScheduledAt, onMinimize, onRestore, onClose, onConfirm }: Props) {
  if (state === "closed") return null;

  const filled = SLOTS.filter(s => block[s.key] !== null).length;
  const ready = filled === 3 && scheduledAt && new Date(scheduledAt) > new Date();

  if (state === "minimized") {
    return (
      <button onClick={onRestore} className="fixed bottom-4 right-4 z-50 bg-amber-500 hover:bg-amber-600 text-white px-3 py-2 rounded-full shadow-lg text-xs flex items-center gap-2">
        📦 Bloque {filled}/3 <span className="text-base">⤴</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={onMinimize}>
      <Card className="w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm flex items-center gap-2"><Calendar className="h-4 w-4" />Bloque de publicación · {filled}/3</h3>
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onMinimize}><Minimize2 className="h-3.5 w-3.5" /></Button>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}><X className="h-3.5 w-3.5" /></Button>
            </div>
          </div>
          <div className="space-y-2">
            {SLOTS.map(s => <Slot key={s.key} icon={s.icon} label={s.label} filled={block[s.key] !== null} preview={block[s.key]?.generated_text} />)}
          </div>
          <div className="space-y-1 pt-2 border-t">
            <Label className="text-xs">Fecha y hora</Label>
            <input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} disabled={filled < 3}
              className="w-full px-2 py-1.5 text-sm border rounded-md bg-background disabled:opacity-50" />
            <p className="text-[10px] text-muted-foreground">{filled < 3 ? "Llená los 3 slots para habilitar la programación" : "Listo para agendar"}</p>
          </div>
          <Button onClick={onConfirm} disabled={!ready} className="w-full gap-1 bg-amber-500 hover:bg-amber-600 text-white">
            <Calendar className="h-4 w-4" />Agendar bloque
          </Button>
        </div>
      </Card>
    </div>
  );
}
