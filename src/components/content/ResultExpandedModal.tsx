import { X, Save, Download, Check, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TYPE_LABELS, AGENDA_TYPES } from "@/lib/content-lab-constants";
import { StoryAgendarButton } from "./StoryAgendarButton";
import { CarouselPreview } from "./CarouselPreview";
import type { ResultV2 } from "./ResultCardV2";

interface Props {
  result: ResultV2 | null;
  onClose: () => void;
  onAgendar: (r: ResultV2) => void;
  onSave: (id: string) => void;
  onDownload: (r: ResultV2) => void;
  onCopy: (r: ResultV2) => void;
}

export function ResultExpandedModal({ result, onClose, onAgendar, onSave, onDownload, onCopy }: Props) {
  if (!result) return null;
  const isImage = result.content_type === "image";
  const isVideo = result.content_type === "video";
  const isCarousel = result.content_type === "carousel";
  const typeLabel = TYPE_LABELS[result.content_type] ?? result.content_type;

  return (
    <div onClick={onClose} className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
      <div onClick={(e) => e.stopPropagation()}
        className="bg-card rounded-lg shadow-2xl max-w-2xl w-full border space-y-3 p-4">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold flex-1">{typeLabel}</h2>
          {result.variation_label && <Badge>{result.variation_label}</Badge>}
          <button onClick={onClose} aria-label="Cerrar" className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
        {/* media (imagen/video/carrusel) entra COMPLETA por alto del viewport (object-contain · sin scroll);
            solo el texto largo scrollea */}
        <div className={isCarousel ? "" : isImage || isVideo ? "flex justify-center" : "max-h-[60vh] overflow-y-auto"}>
          {isImage ? <img src={result.generated_text} alt="" className="rounded-md max-h-[75vh] w-auto object-contain" />
            : isVideo ? <video src={result.generated_text} controls className="rounded-md max-h-[75vh]" />
            : isCarousel ? <CarouselPreview urls={result.media_urls ?? []} caption={result.generated_text} showArrows imgClassName="rounded-md max-h-[70vh] w-auto object-contain" />
            : <p className="text-sm whitespace-pre-wrap leading-relaxed">{result.generated_text}</p>}
        </div>
        {AGENDA_TYPES.has(result.content_type) ? (
          <div className="grid grid-cols-3 gap-2 pt-2">
            <StoryAgendarButton result={result} onAgendar={onAgendar}
              className="bg-amber-500 hover:bg-amber-600 text-white gap-1.5 font-semibold" />{/* mismo diálogo que la tarjeta */}
            <Button variant="outline" onClick={() => isVideo ? null : onSave(result.id)}
              disabled={isVideo}
              title={isVideo ? "Video persistido automáticamente en Storage" : undefined}
              className="gap-1.5">
              {result.saved ? <Check className="h-4 w-4" /> : <Save className="h-4 w-4" />}
              {result.saved ? "Guardado" : isVideo ? "Auto" : "Guardar"}
            </Button>
            <Button variant="outline" onClick={() => onDownload(result)} className="gap-1.5">
              <Download className="h-4 w-4" /> Descargar
            </Button>
          </div>
        ) : (
          <div className="pt-2">
            <Button variant="outline" onClick={() => onCopy(result)} className="w-full gap-1.5">
              <Copy className="h-4 w-4" /> Copiar
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
