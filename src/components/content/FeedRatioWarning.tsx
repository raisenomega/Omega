// F · aviso de ratio de imagen en el modal de Content Lab (cierre del arco modal). Espeja el aviso
// inline de Supervisado (DraftEditForm.tsx:46-61,100-109): si el bloque tiene una IMAGEN cuyo ratio
// (w/h) cae fuera del feed de Instagram Y la red Instagram está marcada en el picker → avisa.
// NO bloquea (mismo criterio que Supervisado): el usuario decide · puede desmarcar IG o agendar
// sabiendo que IG fallará · las demás redes publican igual. Misma regla y umbrales que el backend
// (_media_guard.py) vía feed-aspect.ts. Solo imágenes (los videos van a Reel/Story · lenientes).
import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import type { BlockState } from "@/components/content/ResultCardV2";
import { feedRejectsRatio } from "@/lib/feed-aspect";

export function FeedRatioWarning({ block, igSelected }: { block: BlockState; igSelected: boolean }) {
  // La imagen del bloque (el fan-out comparte 1 media_url · primera imagen · video no aplica).
  const imageUrl = block.items.find(i => i.content_type === "image")?.generated_text ?? null;
  // Ratio real leído del header de la imagen (naturalWidth/Height) · mismo método que DraftEditForm.
  const [ratio, setRatio] = useState<number | null>(null);
  useEffect(() => {
    if (!imageUrl) { setRatio(null); return; }
    const img = new Image();
    img.onload = () => setRatio(img.naturalHeight ? img.naturalWidth / img.naturalHeight : null);
    img.onerror = () => setRatio(null);
    img.src = imageUrl;
    return () => { img.onload = null; img.onerror = null; };
  }, [imageUrl]);

  const feedConflict = ratio !== null && igSelected && feedRejectsRatio("instagram", ratio);
  if (!feedConflict) return null;
  return (
    <div className="flex items-start gap-2 rounded-md border border-amber-500/60 bg-amber-500/10 p-2.5 text-[11px] text-amber-700 dark:text-amber-300">
      <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <span>
        Esta imagen es vertical{ratio ? ` (ratio ${ratio.toFixed(2)})` : ""}. El feed de Instagram la rechaza —
        usá una imagen cuadrada o 4:5, o desmarcá Instagram. Las demás redes publican igual.
      </span>
    </div>
  );
}
