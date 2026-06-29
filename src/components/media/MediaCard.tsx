import { useState } from "react";
import { File as FileIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { MediaCardMenu } from "./MediaCardMenu";
import { MediaPreviewModal } from "./MediaPreviewModal";

export interface MediaFile {
  id: string;
  name: string;
  metadata?: { mimetype?: string; size?: number } | null;
}

interface MediaCardProps {
  file: MediaFile;
  publicUrl: string;
  onDelete: (name: string) => void;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

// Tarjeta de un archivo de la Biblioteca (C1 · extraída del render inline de Media.tsx).
// Thumbnail por tipo: imagen → <img>; video → <video src#t=0.5 preload=metadata muted> que
// pinta el primer frame como preview estático (cero backend); otro → ícono genérico.
// Las acciones viven en un botón [Ver] (primary) en la franja inferior, a la derecha del
// nombre+peso, que abre un mini-menú (MediaCardMenu · C2 + reubicación). Click en el thumbnail
// (zona separada del [Ver]) abre un pop-up de preview (MediaPreviewModal · C3).
export function MediaCard({ file, publicUrl, onDelete }: MediaCardProps) {
  const mime = file.metadata?.mimetype ?? "";
  const isImage = mime.startsWith("image");
  const isVideo = mime.startsWith("video");
  const [preview, setPreview] = useState(false);
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm overflow-hidden group">
      <div
        className="aspect-square bg-secondary flex items-center justify-center relative cursor-pointer"
        onClick={() => setPreview(true)}
      >
        {isImage ? (
          <img src={publicUrl} alt={file.name} className="h-full w-full object-cover" />
        ) : isVideo ? (
          <video src={`${publicUrl}#t=0.5`} preload="metadata" muted playsInline className="h-full w-full object-cover" />
        ) : (
          <FileIcon className="h-12 w-12 text-muted-foreground/30" />
        )}
      </div>
      <CardContent className="p-3 flex items-center justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs font-medium truncate">{file.name}</p>
          <p className="text-xs text-muted-foreground">{formatBytes(file.metadata?.size || 0)}</p>
        </div>
        <MediaCardMenu fileName={file.name} publicUrl={publicUrl} isImage={isImage} onDelete={onDelete} />
      </CardContent>
      <MediaPreviewModal
        open={preview}
        onOpenChange={setPreview}
        name={file.name}
        publicUrl={publicUrl}
        isImage={isImage}
        isVideo={isVideo}
      />
    </Card>
  );
}
