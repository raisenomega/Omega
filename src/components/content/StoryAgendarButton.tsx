// Pieza 3 · botón "Agendar" de la tarjeta con diálogo de placement SOLO para foto vertical 9:16.
// Lee el ratio (new Image()/naturalWidth/Height · espejo de FeedRatioWarning). Si la foto es 9:16
// (ratio < 0.8 · fuera del feed) → diálogo "¿usar en historia? Sí/No" (avisa: el caption no se ve en
// story · IG/FB van como historia, las demás como post normal). Cuadrada/horizontal/no-imagen →
// "Agendar" idéntico a hoy, cero diálogo. El flag is_story viaja en el result al bloque.
import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import type { ResultV2 } from "./result-types";

const STORY_RATIO_MAX = 0.8;  // < 0.8 (w/h) = vertical fuera del feed → candidata a historia (9:16 = 0.56)
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

  const isStoryCandidate = isImage && ratio !== null && ratio < STORY_RATIO_MAX;

  // Foto cuadrada/horizontal/no-imagen → Agendar como hoy (cero diálogo).
  if (!isStoryCandidate) {
    return (
      <Button size="sm" onClick={() => onAgendar(result)} className={BTN}>
        <Calendar className="h-3 w-3" />Agendar
      </Button>
    );
  }

  // 9:16 → diálogo de placement (Sí = historia · No = post normal · ambos agendan · Escape = no agenda).
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button size="sm" className={BTN}><Calendar className="h-3 w-3" />Agendar</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>¿Usar esta imagen en tu historia?</AlertDialogTitle>
          <AlertDialogDescription>
            Es vertical (9:16). En la historia el texto del caption no se muestra. Se publicará como
            historia en Instagram y Facebook, y como post normal en las demás redes marcadas.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={() => onAgendar(result)}>No, post normal</AlertDialogCancel>
          <AlertDialogAction onClick={() => onAgendar({ ...result, is_story: true })}>Sí, historia</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
