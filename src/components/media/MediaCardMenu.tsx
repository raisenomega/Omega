import { useNavigate } from "react-router-dom";
import { Eye, Copy, Wand2, Download, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";

// Media C2 · botón [Ver] (color primary · amarillo de marca) que abre un mini-menú con las 4
// acciones del C1, REUBICADAS del overlay hover. Los handlers son los mismos (cero backend);
// solo cambian de contenedor. "Usar en Content Lab" sigue solo para imágenes.
interface Props {
  fileName: string;
  publicUrl: string;
  isImage: boolean;
  onDelete: (name: string) => void;
}

export function MediaCardMenu({ fileName, publicUrl, isImage, onDelete }: Props) {
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
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          size="sm"
          className="absolute top-2 right-2 h-7 px-2 bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm"
          onClick={(e) => e.stopPropagation()}
        >
          <Eye className="h-3.5 w-3.5 mr-1" />
          Ver
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenuItem onClick={handleCopy}>
          <Copy className="h-4 w-4 mr-2" />
          Copiar
        </DropdownMenuItem>
        {isImage && (
          <DropdownMenuItem onClick={handleUseInContentLab}>
            <Wand2 className="h-4 w-4 mr-2" />
            Usar en Content Lab
          </DropdownMenuItem>
        )}
        <DropdownMenuItem onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Descargar
        </DropdownMenuItem>
        <DropdownMenuItem
          className="text-destructive focus:text-destructive"
          onClick={() => onDelete(fileName)}
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Eliminar
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
