import { MessagesSquare, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { dataAgoLabel } from "@/lib/relative-time";
import { useAeoCheck } from "@/hooks/useAeoCheck";
import { AeoSection } from "./AeoSection";

interface AeoChipProps {
  clientId: string;
}

export function AeoChip({ clientId }: AeoChipProps) {
  const { query, recheck, isRechecking } = useAeoCheck(clientId);

  if (query.isLoading) {
    return (
      <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
        <CardContent className="space-y-3 py-6">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>
    );
  }

  if (query.data && !query.data.analyzed) {
    return (
      <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center gap-3 py-14">
          <MessagesSquare className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground font-body text-center">
            {query.data.message ?? "Todavía no analizamos las preguntas de tu audiencia"}
          </p>
          <Button size="sm" variant="outline" onClick={() => recheck()} disabled={isRechecking}>
            <RefreshCw className={isRechecking ? "animate-spin" : ""} />
            {isRechecking ? "Analizando…" : "Analizar preguntas de mi audiencia"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!query.data) return null;
  const data = query.data;

  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="space-y-5 py-6">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground font-body">{dataAgoLabel(data.generated_at)}</p>
          <Button size="sm" variant="outline" onClick={() => recheck()} disabled={isRechecking}>
            <RefreshCw className={isRechecking ? "animate-spin" : ""} />
            {isRechecking ? "Analizando…" : "Actualizar"}
          </Button>
        </div>

        <AeoSection title="Preguntas frecuentes" items={data.questions} emptyText="Sin preguntas detectadas" />
        <AeoSection title="Tu sitio responde" items={data.answered} emptyText="Tu sitio aún no responde estas preguntas" icon="check" />
        <AeoSection title="Gaps · deberías responder" items={data.gaps} emptyText="Sin gaps detectados" icon="alert" />
        <AeoSection title="Tips" items={data.tips} emptyText="Sin tips por ahora" icon="check" />
      </CardContent>
    </Card>
  );
}
