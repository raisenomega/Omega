// AMBAS · botón "Agendar" con diálogo de placement para TODA imagen (no solo 9:16). Lee el ratio
// (new Image()/naturalWidth/Height · espejo de FeedRatioWarning) solo para adaptar el texto:
//   - apta-feed (ratio ≥ 0.8 · o no medible/fail-open): "¿también en historia?" → No="feed" · Sí="both".
//   - vertical 9:16 (ratio < 0.8): el feed de IG la rechaza → "¿solo historia, o también feed donde
//     la red lo permita?" → "Solo historia"="story" · "También feed"="both".
// No-imagen → "Agendar" plano (cero diálogo). El placement viaja en el result al bloque.
import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import type { ResultV2 } from "./result-types";
import type { Placement } from "@/lib/placement";

const FEED_RATIO_MIN = 0.8;  // < 0.8 (w/h) = vertical fuera del feed de IG (9:16 = 0.56)
const BTN = "bg-amber-500 hover:bg-amber-600 text-white gap-1 flex-1 h-7 text-[11px]";

export function StoryAgendarButton({ result, onAgendar }: { result: ResultV2; onAgendar: (r: ResultV2) => void }) {
  const isImage = result.content_type === "image";
  const [ratio, setRatio] = useState<number | null>(null);
  useEffect(() => {
    if (!isImage || !result.generated_text) { setRatio(null); return; }
    const img = new Image();
    img.onload = () => setRatio(img.naturalHeight ? img.naturalWidth / img.naturalHeight : null);
    img.onerror = () => setRatio(null);
    img.src = result.generated_text;
    return () => { img.onload = null; img.onerror = null; };
  }, [isImage, result.generated_text]);

  const agendar = (placement: Placement) => onAgendar({ ...result, placement });

  // No-imagen → Agendar plano (cero diálogo · texto/video no tienen placement de historia).
  if (!isImage) {
    return <Button size="sm" onClick={() => onAgendar(result)} className={BTN}><Calendar className="h-3 w-3" />Agendar</Button>;
  }

  // fail-open: ratio null (no medible / cargando) → rama apta-feed (asume que entra al feed).
  const isVertical = ratio !== null && ratio < FEED_RATIO_MIN;

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button size="sm" className={BTN}><Calendar className="h-3 w-3" />Agendar</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{isVertical ? "Imagen vertical (9:16)" : "¿Publicar también en historia?"}</AlertDialogTitle>
          <AlertDialogDescription>
            {isVertical
              ? "En Instagram el feed rechaza el 9:16. ¿La publicás solo en historia, o también en el feed donde la red lo permita (Facebook/TikTok)? En la historia el texto del caption no se muestra."
              : "Se publicará en el feed. Si elegís \"también en historia\", se publica además como historia en Instagram y Facebook (en la historia el texto del caption no se muestra)."}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={() => agendar(isVertical ? "story" : "feed")}>
            {isVertical ? "Solo historia" : "No, solo feed"}
          </AlertDialogCancel>
          <AlertDialogAction onClick={() => agendar("both")}>
            {isVertical ? "También feed" : "Sí, también historia"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
