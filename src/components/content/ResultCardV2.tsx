import { Calendar, Save, Download, Check, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TYPE_LABELS } from "@/lib/content-lab-constants";
import { PendingVideoCard } from "./PendingVideoCard";
import { ResearchResultCard } from "./ResearchResultCard";
import type { ResultV2, ModalState, BlockState } from "./result-types";

export type { ResultV2, ModalState, BlockState };

interface Props {
  result: ResultV2;
  onExpand: (r: ResultV2) => void;
  onAgendar: (r: ResultV2) => void;
  onSave: (id: string) => void;
  onDownload: (r: ResultV2) => void;
  onRemove: (id: string) => void;
  onCancel?: (id: string) => void;             // DEBT-CL-010 · pending video
  onUseSnippet?: (snippet: string) => void;    // Brave research · appendea al topic
}

const LABEL_COLORS: Record<string, string> = {
  Conservadora: "bg-slate-500", Balanceada: "bg-blue-500", Atrevida: "bg-rose-500",
};

export function ResultCardV2({ result, onExpand, onAgendar, onSave, onDownload, onRemove, onCancel, onUseSnippet }: Props) {
  // Brave Search · render simplificado en sub-componente
  if (result.content_type === "research") {
    return <ResearchResultCard result={result} onRemove={onRemove} onUseSnippet={onUseSnippet} />;
  }
  // Video pending · placeholder durante generación Veo
  if (result.status === "pending") {
    return <PendingVideoCard resultId={result.id} onCancel={onCancel} />;
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
        {(score > 0 || (result.brand_dna_score ?? 0) > 0) && (
          <div className="flex items-center gap-2 flex-wrap">
            {score > 0 && <Badge className="gap-1 bg-amber-500 text-white text-[10px]">🔥 {score}/100</Badge>}
            {result.virality_estimated && score > 0 && <Badge variant="outline" className="text-[9px]">Estimado</Badge>}
            {(result.brand_dna_score ?? 0) > 0 && <Badge variant="outline" className="text-[9px] border-emerald-500/50 text-emerald-700 dark:text-emerald-400">{Math.round((result.brand_dna_score ?? 0) * 100)}% voz de marca</Badge>}
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
