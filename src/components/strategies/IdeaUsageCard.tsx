import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sparkles, Archive } from "lucide-react";
import { PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { useArchiveIdea } from "@/hooks/useArchiveIdea";
import { DeleteIdeaButton } from "@/components/strategies/DeleteIdeaButton";
import type { UsedIdea } from "@/hooks/useUsedIdeas";

// Fase B.2/C.2/C.3 · tarjeta de una IDEA usada (no una estrategia): red + texto + "De: {título}".
// En Usadas (archived=false): Re-usar + Archivar (PATCH .../archive → la idea pasa a Archivadas).
// En Archivadas (archived=true): Eliminar (DELETE · con confirm obligatorio · C.3). Fallback honesto
// si falta el título. SIN tipo de post (no existe el dato · decisión del owner).
export function IdeaUsageCard({ idea, archived = false }: { idea: UsedIdea; archived?: boolean }) {
  const navigate = useNavigate();
  const archive = useArchiveIdea();
  const red = idea.platform
    ? (PLATFORM_LABELS[idea.platform as keyof typeof PLATFORM_LABELS] ?? idea.platform)
    : "Sin red";
  const origen = idea.strategies?.titulo ?? "(estrategia eliminada)";

  const reusar = () =>
    navigate("/content-lab", { state: { brief: idea.brief, ...(idea.platform ? { platform: idea.platform } : {}) } });

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="p-3 space-y-2">
        <Badge variant="secondary" className="text-[10px]">{red}</Badge>
        {idea.brief && <p className="text-sm line-clamp-4">{idea.brief}</p>}
        <p className="text-[10px] text-muted-foreground line-clamp-1">De: {origen}</p>
        {archived ? (
          <DeleteIdeaButton id={idea.id} />
        ) : (
          <div className="flex gap-1.5">
            <Button size="sm" className="gap-1 h-8 flex-1" onClick={reusar}>
              <Sparkles className="h-3.5 w-3.5" /> Re-usar
            </Button>
            <Button
              size="sm" variant="ghost" className="gap-1 h-8 text-muted-foreground hover:text-destructive"
              disabled={archive.isPending} onClick={() => archive.mutate({ id: idea.id })}
            >
              <Archive className="h-3.5 w-3.5" /> Archivar
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
