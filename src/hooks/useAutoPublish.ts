import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiPost } from "@/lib/api-client";

interface AutoPublishResponse {
  published: boolean;
  platform_post_id: string | null;
  error: string | null;
}

interface AutoPublishInput {
  scheduled_post_id: string;
}

// Auto-publicación real (Publicador agent): ejecuta la publicación de un post YA
// aprobado/programado (status 'pending') vía el token Meta del cliente (OAuth RONDA D).
// Cero fabricación: el backend responde 409 'meta_not_connected' si no hay token,
// 409 'post_not_publishable' si el status no es publicable, y {published:false,error}
// si Meta rechaza. Patrón espejo de useVideoPackCheckout + useUpdatePostStatus.
export function useAutoPublish() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: ({ scheduled_post_id }: AutoPublishInput) =>
      apiPost<AutoPublishResponse>(`/publish/auto`, { scheduled_post_id }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["calendar_list"] });
      if (data.published) {
        toast({ title: "Publicado", description: "El post se publicó en Meta." });
      } else {
        // Meta aceptó la request pero rechazó la publicación: error honesto, no fabricado.
        toast({
          title: "No se pudo publicar",
          description: data.error ?? "Meta rechazó la publicación.",
          variant: "destructive",
        });
      }
    },
    onError: (e: Error) => {
      const msg = e.message;
      const title =
        msg.includes("meta_not_connected") || msg.includes("meta_no_page")
          ? "Conectá Meta primero"
          : msg.includes("post_not_publishable")
            ? "Este post no se puede publicar"
            : msg.includes("post_access_denied")
              ? "Sin acceso a este post"
              : msg.includes("post_not_found")
                ? "Post no encontrado"
                : "No se pudo publicar";
      const description =
        msg.includes("meta_not_connected") || msg.includes("meta_no_page")
          ? "Conectá tu cuenta de Meta en Ajustes para publicar de forma automática."
          : msg.includes("post_not_publishable")
            ? "Solo se pueden auto-publicar posts programados pendientes."
            : msg;
      toast({ title, description, variant: "destructive" });
    },
  });
}
