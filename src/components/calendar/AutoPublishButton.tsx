import { Zap, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAutoPublish } from "@/hooks/useAutoPublish";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

interface AutoPublishButtonProps {
  postId: string;
}

// Botón "Publicar Auto" autocontenido: dispara la auto-publicación real del post
// ya aprobado (status 'pending') vía el hook useAutoPublish. Publica contra el negocio
// ACTIVO del switcher (DEBT-LIMIT1: el backend valida ownership de ese client_id).
// Mismo estilo que el botón "Publicar Manual" hermano (size sm · h-7 · flex-1).
export function AutoPublishButton({ postId }: AutoPublishButtonProps) {
  const autoPublish = useAutoPublish();
  const { activeBusinessId } = useActiveBusiness();
  return (
    <Button
      size="sm"
      variant="secondary"
      className="h-7 flex-1 gap-1 text-[11px]"
      disabled={autoPublish.isPending || !activeBusinessId}
      onClick={() => activeBusinessId && autoPublish.mutate({ scheduled_post_id: postId, client_id: activeBusinessId })}
    >
      {autoPublish.isPending ? (
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      ) : (
        <Zap className="h-3.5 w-3.5" />
      )}
      Publicar Auto
    </Button>
  );
}
