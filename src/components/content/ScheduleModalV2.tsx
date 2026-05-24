import { Minimize2, Calendar, X } from "lucide-react";
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
  onRemoveItem: (i: number) => void;
}

const ICON_BY_TYPE: Record<string, string> = {
  caption: "📝", hashtags: "#", image: "🖼️", video: "🎬",
  email: "✉️", story: "📱", ad: "📢", bio: "👤",
  video_script: "🎬", google_business_post: "🏢", thread: "🧵", carousel: "🎠", linkedin_post: "💼",
};

const MIN_PIECES = 3;
const NON_TEXT = ["image", "video", "hashtags"];
const SPREAD_HOURS = 2;   // LIMITS_OMEGA MIN_HORAS_ENTRE_POSTS
const SPREAD_MAX_DAY = 3; // LIMITS_OMEGA MAX_POSTS_AUTO_PER_DIA_CLIENTE

function computeSpread(base: string, n: number): string[] {
  if (n < 1 || !base) return [];
  const baseDate = new Date(base);
  return Array.from({ length: n }, (_, i) => {
    const day = Math.floor(i / SPREAD_MAX_DAY);
    const inDay = i % SPREAD_MAX_DAY;
    const ts = new Date(baseDate);
    ts.setDate(ts.getDate() + day);
    ts.setHours(ts.getHours() + inDay * SPREAD_HOURS);
    return ts.toLocaleString("es-AR", { dateStyle: "short", timeStyle: "short" });
  });
}

export function ScheduleModalV2({ state, block, scheduledAt, setScheduledAt, onMinimize, onRestore, onClose, onConfirm, onRemoveItem }: Props) {
  if (state === "closed") return null;

  const count = block.items.length;
  const textCount = block.items.filter(i => !NON_TEXT.includes(i.content_type)).length;
  const spread = textCount > 1 && scheduledAt ? computeSpread(scheduledAt, textCount) : [];
  const ready = count >= MIN_PIECES && scheduledAt && new Date(scheduledAt) > new Date() && textCount >= 1;

  if (state === "minimized") {
    return (
      <button onClick={onRestore} className="fixed bottom-4 right-4 z-50 bg-amber-500 hover:bg-amber-600 text-white px-3 py-2 rounded-full shadow-lg text-xs flex items-center gap-2">
        📦 Bloque ({count} {count === 1 ? "pieza" : "piezas"}) <span className="text-base">⤴</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={onMinimize}>
      <Card className="w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm flex items-center gap-2"><Calendar className="h-4 w-4" />Bloque · {count} {count === 1 ? "pieza" : "piezas"} {count >= MIN_PIECES ? "✓" : `(faltan ${MIN_PIECES - count})`}</h3>
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onMinimize}><Minimize2 className="h-3.5 w-3.5" /></Button>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}><X className="h-3.5 w-3.5" /></Button>
            </div>
          </div>
          <div className="space-y-2 max-h-[40vh] overflow-y-auto">
            {count === 0 ? (
              <p className="text-xs text-center text-muted-foreground py-4">Agendá resultados desde las cards para empezar tu bloque</p>
            ) : (
              block.items.map((item, i) => (
                <div key={item.id} className="flex items-center gap-2 p-2 rounded-md border border-emerald-300 bg-emerald-50 dark:bg-emerald-950/30">
                  <span className="text-lg">{ICON_BY_TYPE[item.content_type] ?? "📄"}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium capitalize">{item.content_type}</p>
                    <p className="text-[10px] text-muted-foreground truncate">{item.generated_text.slice(0, 80)}</p>
                  </div>
                  <button onClick={() => onRemoveItem(i)} className="text-muted-foreground hover:text-destructive" aria-label="Quitar"><X className="h-3.5 w-3.5" /></button>
                </div>
              ))
            )}
          </div>
          <div className="space-y-1 pt-2 border-t">
            <Label className="text-xs">Fecha y hora</Label>
            <input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} disabled={count < MIN_PIECES}
              className="w-full px-2 py-1.5 text-sm border rounded-md bg-background disabled:opacity-50" />
            <p className="text-[10px] text-muted-foreground">{count < MIN_PIECES ? `Necesitás ${MIN_PIECES - count} pieza(s) más para activar` : `Listo · ${textCount} post${textCount === 1 ? "" : "s"} (1 row por item de texto)`}</p>
            {spread.length > 1 && (
              <div className="text-[10px] text-amber-700 dark:text-amber-300 pt-1 border-l-2 border-amber-400 pl-2 space-y-0.5">
                <div className="font-medium">Spread automático ({SPREAD_HOURS}h gap · max {SPREAD_MAX_DAY}/día):</div>
                {spread.map((s, i) => <div key={i}>· #{i + 1} → {s}</div>)}
              </div>
            )}
          </div>
          <Button onClick={onConfirm} disabled={!ready} className="w-full gap-1 bg-amber-500 hover:bg-amber-600 text-white">
            <Calendar className="h-4 w-4" />Agendar bloque
          </Button>
        </div>
      </Card>
    </div>
  );
}
