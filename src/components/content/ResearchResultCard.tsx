import { Search, Plus, ExternalLink, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { ResultV2 } from "./ResultCardV2";

interface Props {
  result: ResultV2;
  onRemove: (id: string) => void;
  onUseSnippet?: (snippet: string) => void;
}

// Card especializada para resultados de Brave Search (content_type='research').
// Render simplificado · sin Save/Agendar/Download (no aplican).
// Spec owner: "resultado pop-up como resultado de generar cualquier type".
export function ResearchResultCard({ result, onRemove, onUseSnippet }: Props) {
  const snippet = result.snippet ?? result.generated_text;
  const title = result.title ?? result.url ?? "Resultado web";

  return (
    <Card className="relative h-full border-blue-500/30 hover:border-blue-500 hover:shadow-md transition bg-blue-50/30 dark:bg-blue-950/20">
      <button onClick={() => onRemove(result.id)}
        className="absolute top-1.5 right-1.5 h-6 w-6 rounded-full flex items-center justify-center hover:bg-muted text-muted-foreground hover:text-foreground transition z-10"
        aria-label="Eliminar resultado">
        <X className="h-3.5 w-3.5" />
      </button>
      <CardContent className="p-3 pr-8 space-y-2 flex flex-col h-full">
        <div className="flex items-center gap-1.5">
          <Search className="h-3.5 w-3.5 text-blue-600 shrink-0" />
          <Badge variant="outline" className="text-[10px] border-blue-400 text-blue-700 dark:text-blue-300">research</Badge>
        </div>
        {result.url ? (
          <a href={result.url} target="_blank" rel="noopener noreferrer"
            className="text-xs font-medium text-blue-700 dark:text-blue-300 hover:underline line-clamp-2 flex items-start gap-1">
            {title}
            <ExternalLink className="h-3 w-3 opacity-60 shrink-0 mt-0.5" />
          </a>
        ) : <p className="text-xs font-medium">{title}</p>}
        <p className="text-[11px] text-muted-foreground line-clamp-3 flex-1">{snippet}</p>
        <div className="flex gap-1 pt-1">
          {onUseSnippet && (
            <Button size="sm" onClick={() => onUseSnippet(snippet)}
              className="bg-blue-600 hover:bg-blue-700 text-white gap-1 flex-1 h-7 text-[11px]">
              <Plus className="h-3 w-3" /> Usar snippet
            </Button>
          )}
          {result.url && (
            <Button size="sm" variant="outline" asChild className="gap-1 flex-1 h-7 text-[11px]">
              <a href={result.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-3 w-3" /> Visitar
              </a>
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
