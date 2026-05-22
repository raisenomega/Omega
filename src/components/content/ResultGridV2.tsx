import { Card, CardContent } from "@/components/ui/card";
import { FileText } from "lucide-react";
import { ResultCardV2, type ResultV2 } from "@/components/content/ResultCardV2";

interface Props {
  results: ResultV2[];
  onAgendar: (r: ResultV2) => void;
  onSave: (id: string) => void;
  onDownload: (r: ResultV2) => void;
}

export function ResultGridV2({ results, onAgendar, onSave, onDownload }: Props) {
  if (results.length === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center gap-2 py-10 text-center">
          <FileText className="h-10 w-10 text-muted-foreground/30" />
          <p className="text-sm font-medium">Sin resultados todavía</p>
          <p className="text-xs text-muted-foreground">
            Completá el prompt y dale "Generar con ARIA" · los resultados se acumulan acá.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs uppercase tracking-wider text-muted-foreground">
        Resultados acumulados · {results.length}
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {results.map((r) => (
          <ResultCardV2 key={r.id} result={r} onAgendar={onAgendar} onSave={onSave} onDownload={onDownload} />
        ))}
      </div>
    </div>
  );
}
