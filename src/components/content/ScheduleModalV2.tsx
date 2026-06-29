import { Minimize2, Calendar, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import type { ModalState, BlockState } from "@/components/content/ResultCardV2";
import { computeSpread, SPREAD_HOURS, SPREAD_MAX_DAY } from "@/lib/schedule-spread";
import { MEDIA_TYPES } from "@/hooks/useScheduleBlock";
import { NetworkPicker } from "@/components/content/NetworkPicker";
import { FeedRatioWarning } from "@/components/content/FeedRatioWarning";
import { BlockItemPreview } from "@/components/content/BlockItemPreview";
import { placementPubCount } from "@/lib/placement";
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
  connectedNetworks: string[];      // E · redes active del negocio (fan-out picker)
  selectedPlatforms: string[];      // E · redes marcadas (siembra form.platform · Opción 2)
  onTogglePlatform: (p: string) => void;
  loading?: boolean;  // BUG 11 jun · request en vuelo → botón con spinner (no parece colgado)
}

const MIN_PIECES = 2;  // mínimo real = 1 caption + 1 imagen/video (no 2 piezas cualquiera)
const NON_TEXT = ["image", "video", "hashtags", "carousel"];  // el carrusel = media (N placas) · NO infla el conteo de texto

export function ScheduleModalV2({ state, block, scheduledAt, setScheduledAt, onMinimize, onRestore, onClose, onConfirm, onRemoveItem, connectedNetworks, selectedPlatforms, onTogglePlatform, loading = false }: Props) {
  if (state === "closed") return null;
  const count = block.items.length;
  const textCount = block.items.filter(i => !NON_TEXT.includes(i.content_type)).length;
  const mediaCount = block.items.filter(i => MEDIA_TYPES.includes(i.content_type)).length;
  const hasCarousel = block.items.some(i => i.content_type === "carousel");  // F.3 · trae sus N placas (es media)
  const hasMin = hasCarousel || (textCount >= 1 && mediaCount >= 1);  // carrusel (solo o con caption) · o caption+media
  const missing = hasMin ? "" : textCount < 1 && mediaCount < 1 ? "1 caption + 1 imagen/video" : textCount < 1 ? "1 caption" : "1 imagen/video";
  const spread = textCount > 1 && scheduledAt ? computeSpread(scheduledAt, textCount) : [];
  const validNetworks = selectedPlatforms.filter(p => connectedNetworks.includes(p));  // E · doble guarda front
  const ready = hasMin && scheduledAt && new Date(scheduledAt) > new Date() && validNetworks.length >= 1;
  const imgPlacement = block.items.find(i => i.content_type === "image")?.placement ?? "feed";  // AMBAS
  // piezas reales = captions; carrusel-solo (sin caption) = 1 pieza (su título). El carrusel acompaña como media.
  const pieceCount = textCount > 0 ? textCount : (hasCarousel ? 1 : 0);
  const realPosts = pieceCount * validNetworks.reduce((s, n) => s + placementPubCount(imgPlacement, n), 0);

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
                  <BlockItemPreview item={item} />
                  <button onClick={() => onRemoveItem(i)} className="text-muted-foreground hover:text-destructive" aria-label="Quitar"><X className="h-3.5 w-3.5" /></button>
                </div>
              ))
            )}
          </div>
          <div className="pt-2 border-t space-y-2"><NetworkPicker networks={connectedNetworks} selected={selectedPlatforms} onToggle={onTogglePlatform} /><FeedRatioWarning block={block} igSelected={selectedPlatforms.includes("instagram")} /></div>
          <div className="space-y-1 pt-2 border-t">
            <Label className="text-xs">Fecha y hora</Label>
            <input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} disabled={!hasMin}
              className="w-full px-2 py-1.5 text-sm border rounded-md bg-background disabled:opacity-50" />
            <p className="text-[10px] text-muted-foreground">{!hasMin ? `Necesitás ${missing} (mín. ${MIN_PIECES}: caption + media)` : `Listo · ${realPosts} publicación${realPosts === 1 ? "" : "es"} (${pieceCount} ${pieceCount === 1 ? "pieza" : "piezas"} × ${validNetworks.length} red${validNetworks.length === 1 ? "" : "es"}${imgPlacement === "both" ? " · feed+historia" : ""})`}</p>
            {spread.length > 1 && (
              <div className="text-[10px] text-amber-700 dark:text-amber-300 pt-1 border-l-2 border-amber-400 pl-2 space-y-0.5">
                <div className="font-medium">Spread automático ({SPREAD_HOURS}h gap · max {SPREAD_MAX_DAY}/día):</div>
                {spread.map((s, i) => <div key={i}>· #{i + 1} → {s}</div>)}
              </div>
            )}
          </div>
          <p className="text-[10px] text-muted-foreground">Este bloque se programa en el calendario · REX lo publica automáticamente a la hora elegida.</p>
          <Button onClick={onConfirm} disabled={!ready || loading} className="w-full gap-1 bg-amber-500 hover:bg-amber-600 text-white">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calendar className="h-4 w-4" />}{loading ? "Agendando…" : "Agendar bloque"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
