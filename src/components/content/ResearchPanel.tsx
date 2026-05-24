import { ExternalLink, Plus, Search, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { ResearchResult } from "@/hooks/useResearch";

interface Props {
  query?: string;
  results?: ResearchResult[];
  isLoading?: boolean;
  durationMs?: number;
  onDismiss: () => void;
  onUseSnippet: (snippet: string) => void;
}

// Panel inline arriba del grid · siempre visible mientras existan results
// o esté loading · dismiss con X. Click "Usar snippet" appendea al topic
// textarea (caller decide · explícito y predecible · spec Brave A+A+A).
export function ResearchPanel({ query, results, isLoading, durationMs, onDismiss, onUseSnippet }: Props) {
  const showLoading = isLoading;
  const hasResults = (results?.length ?? 0) > 0;
  if (!showLoading && !hasResults) return null;

  return (
    <Card className="border-blue-500/30 bg-blue-50/30 dark:bg-blue-950/20">
      <CardContent className="p-3 space-y-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <Search className="h-4 w-4 text-blue-600 shrink-0" />
            <span className="text-xs font-medium truncate">
              {showLoading
                ? `Buscando "${query}"…`
                : `${results?.length ?? 0} resultados · ${durationMs ?? 0}ms · "${query}"`}
            </span>
          </div>
          <button onClick={onDismiss} className="h-6 w-6 rounded hover:bg-blue-100 dark:hover:bg-blue-900/40 flex items-center justify-center shrink-0" aria-label="Cerrar panel">
            <X className="h-3.5 w-3.5 text-muted-foreground" />
          </button>
        </div>
        {showLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
          </div>
        )}
        {hasResults && (
          <div className="space-y-2 max-h-[260px] overflow-y-auto">
            {results!.map((r, i) => (
              <div key={i} className="border-l-2 border-blue-300 pl-2 space-y-1">
                <a href={r.url} target="_blank" rel="noopener noreferrer"
                  className="text-xs font-medium text-blue-700 dark:text-blue-300 hover:underline flex items-center gap-1">
                  {r.title || r.url}
                  <ExternalLink className="h-3 w-3 opacity-60" />
                </a>
                <p className="text-[11px] text-muted-foreground line-clamp-2">{r.snippet}</p>
                <Button size="sm" variant="outline" onClick={() => onUseSnippet(r.snippet)}
                  className="h-6 text-[10px] gap-1 px-2">
                  <Plus className="h-3 w-3" /> Usar snippet
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
