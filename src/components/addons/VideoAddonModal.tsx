/**
 * @deprecated 23 may 2026 — Video Packs migrados a página dedicada /add-ons.
 * El sidebar entry "Add-Ons" + ContentLabFormBar botón "Video Packs" (cuando
 * type === 'video') ahora navegan a /add-ons en vez de abrir este modal.
 * Mantener temporalmente por si se quiere revivir como modal contextual.
 * Eliminar en Sprint 4 si no encuentra uso.
 */
import { useState } from "react";
import { Video } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { VideoPackCard } from "./VideoPackCard";
import { VIDEO_PACKS } from "./_video_packs_data";

export function VideoAddonModal() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();

  const handleActivate = (packName: string) => {
    toast({
      title: "Próximamente",
      description: `${packName} estará disponible vía Stripe pronto. Contáctanos para acceso anticipado.`,
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Video className="h-4 w-4" />
          Agregar Video Pack
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Video Packs · Veo 3.1 + ARIA</DialogTitle>
          <DialogDescription>
            Elegí el pack que mejor encaja con tu volumen de video.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 md:grid-cols-3">
          {VIDEO_PACKS.map((p) => (
            <VideoPackCard
              key={p.name}
              name={p.name}
              price={p.price}
              bullets={p.bullets}
              idealFor={p.idealFor}
              onActivate={() => handleActivate(p.name)}
            />
          ))}
        </div>
        <p className="text-xs text-muted-foreground text-center border-t pt-3">
          Todos los packs incluyen audio nativo · generación con Veo 3.1 · sin videos sueltos
        </p>
      </DialogContent>
    </Dialog>
  );
}
