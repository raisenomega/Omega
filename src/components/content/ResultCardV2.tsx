import { Calendar, Save, Download, Check, X, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TYPE_LABELS } from "@/lib/content-lab-constants";

export interface ResultV2 {
  id: string;
  generated_text: string;
  content_type: string;
  variation_label?: string;
  virality_score?: number;
  virality_estimated?: boolean;
  saved?: boolean;
  status?: "pending" | "completed" | "failed";
}

export type ModalState = "closed" | "open" | "minimized";
export interface BlockState { caption: ResultV2 | null; image: ResultV2 | null; hashtags: ResultV2 | null }

interface Props {
  result: ResultV2;
  onExpand: (r: ResultV2) => void;
  onAgendar: (r: ResultV2) => void;
  onSave: (id: string) => void;
  onDownload: (r: ResultV2) => void;
  onRemove: (id: string) => void;
}

const LABEL_COLORS: Record<string, string> = {
  Conservadora: "bg-slate-500", Balanceada: "bg-blue-500", Atrevida: "bg-rose-500",
};

export function ResultCardV2({ result, onExpand, onAgendar, onSave, onDownload, onRemove }: Props) {
  if (result.status === "pending") {
    return (
      <Card className="relative h-full border-amber-500/30 flex flex-col items-center justify-center gap-2 p-4">
        <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
        <p className="text-xs text-center text-muted-foreground">ARIA está generando tu video...</p>
        <p className="text-[10px] text-center text-muted-foreground/60">~30-90 segundos</p>
      </Card>
    );
  }

  const isImage = result.content_type === "image";
  const isVideo = result.content_type === "video";
  const score = result.virality_score ?? 0;
  const labelClass = result.variation_label ? LABEL_COLORS[result.variation_label] ?? "bg-amber-500" : "bg-amber-500";
  const typeLabel = TYPE_LABELS[result.content_type] ?? result.content_type;

  return (
    <Card onClick={() => onExpand(result)}
      className="relative h-full overflow-hidden border-amber-500/30 cursor-pointer hover:border-amber-500 hover:shadow-md transition group">
      <button onClick={(e) => { e.stopPropagation(); onRemove(result.id); }}
        className="absolute top-1.5 right-1.5 h-6 w-6 rounded-full flex items-center justify-center hover:bg-muted text-muted-foreground hover:text-foreground transition z-10"
        aria-label="Eliminar resultado">
        <X className="h-3.5 w-3.5" />
      </button>
      <CardContent className="p-3 pr-8 space-y-2">
        <div className="flex items-center justify-between gap-2">
          <Badge variant="outline" className="text-[10px]">{typeLabel}</Badge>
          {result.variation_label && (
            <Badge className={`${labelClass} text-white text-[10px] px-2`}>{result.variation_label}</Badge>
          )}
        </div>
        {isImage ? <img src={result.generated_text} alt="" className="rounded-md w-full max-h-[100px] object-cover" />
          : isVideo ? <video src={result.generated_text} controls className="rounded-md w-full max-h-[100px] object-cover" />
          : <p className="text-sm line-clamp-3 whitespace-pre-wrap">{result.generated_text}</p>}
        {score > 0 && (
          <div className="flex items-center gap-2">
            <Badge className="gap-1 bg-amber-500 text-white text-[10px]">🔥 {score}/100</Badge>
            {result.virality_estimated && <Badge variant="outline" className="text-[9px]">Estimado</Badge>}
          </div>
        )}
        <p className="text-[10px] text-amber-600 opacity-0 group-hover:opacity-100 transition">clic para expandir →</p>
        <div className="flex gap-1 pt-1" onClick={(e) => e.stopPropagation()}>
          <Button size="sm" onClick={() => onAgendar(result)}
            className="bg-amber-500 hover:bg-amber-600 text-white gap-1 flex-1 h-7 text-[11px]">
            <Calendar className="h-3 w-3" />Agendar
          </Button>
          <Button size="sm" variant="outline" onClick={() => isVideo ? null : onSave(result.id)}
            disabled={isVideo}
            title={isVideo ? "Video persistido automáticamente en Storage" : undefined}
            className={`gap-1 flex-1 h-7 text-[11px] ${result.saved ? "bg-emerald-600 hover:bg-emerald-700 text-white border-emerald-600" : ""}`}>
            {result.saved ? <Check className="h-3 w-3" /> : <Save className="h-3 w-3" />}
            {result.saved ? "✓" : isVideo ? "Auto" : "Guardar"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => onDownload(result)} className="gap-1 flex-1 h-7 text-[11px]">
            <Download className="h-3 w-3" />Descargar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
