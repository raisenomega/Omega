import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";

// Media C3 · pop-up de preview al hacer click en el thumbnail. Se adapta al tipo:
// imagen → <img object-contain> completa sin scroll; video → <video controls> que REPRODUCE
// (no solo el primer frame). Cero backend: reusa la misma url pública del thumbnail.
interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  name: string;
  publicUrl: string;
  isImage: boolean;
  isVideo: boolean;
}

export function MediaPreviewModal({ open, onOpenChange, name, publicUrl, isImage, isVideo }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[92vw] sm:max-w-3xl p-2 bg-background border-border/50">
        <DialogTitle className="sr-only">{name}</DialogTitle>
        <DialogDescription className="sr-only">Vista previa de {name}</DialogDescription>
        {isImage ? (
          <img
            src={publicUrl}
            alt={name}
            className="mx-auto h-auto w-auto object-contain max-h-[90vh] max-w-[90vw]"
          />
        ) : isVideo ? (
          <video
            src={publicUrl}
            controls
            playsInline
            className="mx-auto w-auto object-contain max-h-[90vh] max-w-[90vw]"
          />
        ) : (
          <p className="py-12 text-center text-sm text-muted-foreground">
            No hay vista previa para este archivo.
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}
