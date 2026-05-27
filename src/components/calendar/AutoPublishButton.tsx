import { Zap, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAutoPublish } from "@/hooks/useAutoPublish";

interface AutoPublishButtonProps {
  postId: string;
}

// Botón "Publicar Auto" autocontenido: dispara la auto-publicación real del post
// ya aprobado (status 'pending') vía el hook useAutoPublish. Reemplaza el placeholder
// deshabilitado de PostsList (cero-mocks: ahora publica de verdad o falla honesto).
// Mismo estilo que el botón "Publicar Manual" hermano (size sm · h-7 · flex-1).
export function AutoPublishButton({ postId }: AutoPublishButtonProps) {
  const autoPublish = useAutoPublish();
  return (
    <Button
      size="sm"
      variant="secondary"
      className="h-7 flex-1 gap-1 text-[11px]"
      disabled={autoPublish.isPending}
      onClick={() => autoPublish.mutate({ scheduled_post_id: postId })}
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
