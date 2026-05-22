import { Calendar, Save, Download, Check } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export interface ResultV2 {
  id: string;
  generated_text: string;
  content_type: string;
  variation_label?: string;  // "Conservadora" | "Balanceada" | "Atrevida"
  virality_score?: number;
  virality_estimated?: boolean;
  saved?: boolean;
}

export type ModalState = "closed" | "open" | "minimized";
export interface BlockState { caption: ResultV2 | null; image: ResultV2 | null; hashtags: ResultV2 | null }

interface Props {
  result: ResultV2;
  onAgendar: (r: ResultV2) => void;
  onSave: (id: string) => void;
  onDownload: (r: ResultV2) => void;
}

const LABEL_COLORS: Record<string, string> = {
  Conservadora: "bg-slate-500", Balanceada: "bg-blue-500", Atrevida: "bg-rose-500",
};

export function ResultCardV2({ result, onAgendar, onSave, onDownload }: Props) {
  const isImage = result.content_type === "image";
  const isVideo = result.content_type === "video";
  const score = result.virality_score ?? 0;
  const labelClass = result.variation_label ? LABEL_COLORS[result.variation_label] ?? "bg-amber-500" : "bg-amber-500";

  return (
    <Card className="border-amber-500/30">
      <CardContent className="p-3 space-y-2">
        {result.variation_label && (
          <Badge className={`${labelClass} text-white text-[10px] px-2`}>{result.variation_label}</Badge>
        )}
        {isImage ? (
          <img src={result.generated_text} alt="" className="rounded-md w-full" />
        ) : isVideo ? (
          <video src={result.generated_text} controls className="rounded-md w-full" />
        ) : (
          <p className="text-sm whitespace-pre-wrap">{result.generated_text}</p>
        )}
        {score > 0 && (
          <div className="flex items-center gap-2">
            <Badge className="gap-1 bg-amber-500 text-white text-[10px]">🔥 {score}/100</Badge>
            {result.virality_estimated && <Badge variant="outline" className="text-[9px]">Estimado</Badge>}
          </div>
        )}
        <div className="flex gap-1.5 pt-1">
          <Button size="sm" variant="default" onClick={() => onAgendar(result)} className="gap-1 flex-1 h-8 text-xs">
            <Calendar className="h-3.5 w-3.5" />Agendar
          </Button>
          <Button size="sm" variant={result.saved ? "default" : "outline"} onClick={() => onSave(result.id)}
            className={`gap-1 flex-1 h-8 text-xs ${result.saved ? "bg-emerald-600 hover:bg-emerald-700" : ""}`}>
            {result.saved ? <Check className="h-3.5 w-3.5" /> : <Save className="h-3.5 w-3.5" />}
            {result.saved ? "Guardado" : "Guardar"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => onDownload(result)} className="gap-1 flex-1 h-8 text-xs">
            <Download className="h-3.5 w-3.5" />Descargar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
