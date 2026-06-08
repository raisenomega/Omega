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
  client_id: string;  // negocio ACTIVO del switcher (Switcher V1 · DEBT-LIMIT1)
}

// Mensajes §8 (cero jerga · cero codigo crudo en pantalla) para los estados de publicacion via Zernio.
// Config faltante (gate 4xx · post sigue pending, reintentable) y fallo real comparten este mapeo.
function zernioMessage(code: string): { title: string; description: string } {
  if (code.includes("zernio_sin_cuenta") || code.includes("sin_red"))
    return { title: "Conectá la red primero", description: "No hay una cuenta conectada para esta red. Conectala y volvé a intentar." };
  if (code.includes("zernio_cuenta_ambigua"))
    return { title: "Hay varias cuentas para esta red", description: "Conectá una sola cuenta para esta red para publicar de forma automática." };
  if (code.includes("imagen_vertical_no_apta_feed_ig"))
    return { title: "Imagen vertical para el feed de Instagram", description: "El feed de Instagram no acepta imágenes verticales (9:16). Usá una cuadrada o 4:5, o publicala como Reel/Story. Las demás redes publican igual." };
  if (code.includes("zernio_media_requerida"))
    return { title: "Falta imagen o video", description: "Esta red necesita una imagen o video y el post no la tiene." };
  if (code.includes("zernio_api_key_ausente"))
    return { title: "Publicación no configurada", description: "La publicación automática todavía no está disponible." };
  if (code.includes("post_not_publishable"))
    return { title: "Este post no se puede publicar", description: "Solo se pueden auto-publicar posts programados pendientes." };
  if (code.includes("post_access_denied"))
    return { title: "Sin acceso a este post", description: "No tenés permiso sobre este post." };
  if (code.includes("post_not_found"))
    return { title: "Post no encontrado", description: "El post ya no existe." };
  return { title: "No se pudo publicar", description: "La red rechazó la publicación. Intentá de nuevo más tarde." };
}

// Auto-publicacion real (Publicador agent) via Zernio: publica un post YA aprobado (status 'pending').
// Cero fabricacion: config faltante → 409 (el post sigue pending, reintentable) · fallo real de
// publicacion → {published:false, error}. Ningun camino finge exito. Patron espejo de useUpdatePostStatus.
export function useAutoPublish() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: ({ scheduled_post_id, client_id }: AutoPublishInput) =>
      apiPost<AutoPublishResponse>(`/publish/auto`, { scheduled_post_id, client_id }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["calendar_list"] });
      if (data.published) {
        toast({ title: "Publicado", description: "El post se publicó." });
      } else {
        // El intento real de publicar se hizo pero la red lo rechazo: error honesto §8, no fabricado.
        const m = zernioMessage(data.error ?? "");
        toast({ title: m.title, description: m.description, variant: "destructive" });
      }
    },
    onError: (e: Error) => {
      // Gate 4xx (config faltante · el post sigue pending y reintentable) → mensaje §8 legible.
      const m = zernioMessage(e.message);
      toast({ title: m.title, description: m.description, variant: "destructive" });
    },
  });
}
