import { Minimize2, Calendar, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import type { ModalState, BlockState } from "@/components/content/ResultCardV2";
import { computeSpread, SPREAD_HOURS, SPREAD_MAX_DAY } from "@/lib/schedule-spread";
import { MEDIA_TYPES } from "@/hooks/useScheduleBlock";

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
  loading?: boolean;  // BUG 11 jun · request en vuelo → botón con spinner (no parece colgado)
}

const ICON_BY_TYPE: Record<string, string> = {
  caption: "📝", hashtags: "#", image: "🖼️", video: "🎬",
  email: "✉️", story: "📱", ad: "📢", bio: "👤",
  video_script: "🎬", google_business_post: "🏢", thread: "🧵", carousel: "🎠", linkedin_post: "💼",
};

const MIN_PIECES = 2;  // mínimo real = 1 caption + 1 imagen/video (no 2 piezas cualquiera)
const NON_TEXT = ["image", "video", "hashtags"];

export function ScheduleModalV2({ state, block, scheduledAt, setScheduledAt, onMinimize, onRestore, onClose, onConfirm, onRemoveItem, loading = false }: Props) {
  if (state === "closed") return null;

  const count = block.items.length;
  const textCount = block.items.filter(i => !NON_TEXT.includes(i.content_type)).length;
  const mediaCount = block.items.filter(i => MEDIA_TYPES.includes(i.content_type)).length;
  const hasMin = textCount >= 1 && mediaCount >= 1;  // 1 caption + 1 imagen/video
  const missing = hasMin ? "" : textCount < 1 && mediaCount < 1 ? "1 caption + 1 imagen/video" : textCount < 1 ? "1 caption" : "1 imagen/video";
  const spread = textCount > 1 && scheduledAt ? computeSpread(scheduledAt, textCount) : [];
  const ready = hasMin && scheduledAt && new Date(scheduledAt) > new Date();

  if (state === "minimized") {
    return (
      <button onClick={onRestore} className="fixed bottom-4 right-4 z-50 bg-amber-500 hover:bg-amber-600 text-white px-3 py-2 rounded-full shadow-lg text-xs flex items-center gap-2">
        📦 Bloque ({count} {count === 1 ? "pieza" : "piezas"}) <span className="text-base">⤴</span>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={onMinimize}>
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm flex items-center gap-2"><Calendar className="h-4 w-4" />Bloque · {count} {count === 1 ? "pieza" : "piezas"} {hasMin ? "✓" : `· falta ${missing}`}</h3>
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onMinimize}><Minimize2 className="h-3.5 w-3.5" /></Button>
              <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onClose}><X className="h-3.5 w-3.5" /></Button>
            </div>
          </div>
          <div className="space-y-2 max-h-[55vh] overflow-y-auto">
            {count === 0 ? (
              <p className="text-xs text-center text-muted-foreground py-4">Agendá resultados desde las cards para empezar tu bloque</p>
            ) : (
              block.items.map((item, i) => (
                <div key={item.id} className="flex items-center gap-2 p-2 rounded-md border border-emerald-300 bg-emerald-50 dark:bg-emerald-950/30">
                  <span className="text-lg">{ICON_BY_TYPE[item.content_type] ?? "📄"}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium capitalize">{item.content_type}</p>
                    {item.content_type === "image" ? <img src={item.generated_text} alt="" className="h-16 w-16 rounded object-cover" />
                      : item.content_type === "video" ? <video src={item.generated_text} className="h-16 w-16 rounded object-cover" />
                      : <p className="text-[10px] text-muted-foreground truncate">{item.generated_text.slice(0, 80)}</p>}
                  </div>
                  <button onClick={() => onRemoveItem(i)} className="text-muted-foreground hover:text-destructive" aria-label="Quitar"><X className="h-3.5 w-3.5" /></button>
                </div>
              ))
            )}
          </div>
          <div className="space-y-1 pt-2 border-t">
            <Label className="text-xs">Fecha y hora</Label>
            <input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} disabled={!hasMin}
              className="w-full px-2 py-1.5 text-sm border rounded-md bg-background disabled:opacity-50" />
            <p className="text-[10px] text-muted-foreground">{!hasMin ? `Necesitás ${missing} (mín. ${MIN_PIECES}: caption + media)` : `Listo · ${textCount} post${textCount === 1 ? "" : "s"} (1 row por item de texto)`}</p>
            {spread.length > 1 && (
              <div className="text-[10px] text-amber-700 dark:text-amber-300 pt-1 border-l-2 border-amber-400 pl-2 space-y-0.5">
                <div className="font-medium">Spread automático ({SPREAD_HOURS}h gap · max {SPREAD_MAX_DAY}/día):</div>
                {spread.map((s, i) => <div key={i}>· #{i + 1} → {s}</div>)}
              </div>
            )}
          </div>
          <Button onClick={onConfirm} disabled={!ready || loading} className="w-full gap-1 bg-amber-500 hover:bg-amber-600 text-white">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calendar className="h-4 w-4" />}{loading ? "Agendando…" : "Agendar bloque"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
