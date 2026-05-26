import { useNavigate } from "react-router-dom";
import { Copy, Wand2, Download, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

// TAREA 2 · grupo de acciones en hover de cada card de la galería Media.
// Frontend only · delete ya existe client-side (handleDelete prop).
interface Props {
  fileName: string;
  publicUrl: string;
  isImage: boolean;
  onDelete: (name: string) => void;
}

export function MediaCardActions({ fileName, publicUrl, isImage, onDelete }: Props) {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(publicUrl);
      toast({ title: "URL copiada" });
    } catch {
      toast({ title: "No se pudo copiar la URL", variant: "destructive" });
    }
  };

  const handleUseInContentLab = () => {
    navigate("/content-lab", { state: { referenceImageUrl: publicUrl } });
  };

  const handleDownload = async () => {
    try {
      const res = await fetch(publicUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const objectUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = objectUrl;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(objectUrl);
    } catch {
      toast({ title: "Error al descargar", variant: "destructive" });
    }
  };

  return (
    <div className="absolute inset-0 bg-background/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
      <Button variant="ghost" size="icon" className="h-8 w-8" title="Copiar URL" onClick={handleCopy}>
        <Copy className="h-4 w-4" />
      </Button>
      {isImage && (
        <Button variant="ghost" size="icon" className="h-8 w-8" title="Usar en Content Lab" onClick={handleUseInContentLab}>
          <Wand2 className="h-4 w-4" />
        </Button>
      )}
      <Button variant="ghost" size="icon" className="h-8 w-8" title="Descargar" onClick={handleDownload}>
        <Download className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-destructive hover:text-destructive"
        title="Eliminar"
        onClick={() => onDelete(fileName)}
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
