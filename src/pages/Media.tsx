import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import {
  ImageIcon,
  Upload,
  Loader2,
  Trash2,
  Search,
  FileImage,
  FileVideo,
  File,
} from "lucide-react";

function getFileIcon(type: string) {
  if (type.startsWith("image")) return FileImage;
  if (type.startsWith("video")) return FileVideo;
  return File;
}

function formatBytes(bytes: number) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function Media() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);

  const { data: files, isLoading } = useQuery({
    queryKey: ["media-files"],
    queryFn: async () => {
      const { data, error } = await supabase.storage
        .from("media")
        .list("", { limit: 200, sortBy: { column: "created_at", order: "desc" } });
      if (error) throw error;
      return data ?? [];
    },
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadFiles = e.target.files;
    if (!uploadFiles || uploadFiles.length === 0) return;

    setUploading(true);
    try {
      for (const file of Array.from(uploadFiles)) {
        const fileName = `${Date.now()}-${file.name}`;
        const { error } = await supabase.storage
          .from("media")
          .upload(fileName, file);
        if (error) throw error;
      }
      queryClient.invalidateQueries({ queryKey: ["media-files"] });
      toast({ title: `${uploadFiles.length} archivo(s) subido(s)` });
    } catch (err: any) {
      toast({ title: "Error al subir", description: err.message, variant: "destructive" });
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDelete = async (name: string) => {
    const { error } = await supabase.storage.from("media").remove([name]);
    if (error) {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    } else {
      queryClient.invalidateQueries({ queryKey: ["media-files"] });
      toast({ title: "Archivo eliminado" });
    }
  };

  const filtered = (files ?? []).filter((f) =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  const getPublicUrl = (name: string) =>
    supabase.storage.from("media").getPublicUrl(name).data.publicUrl;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold tracking-tight">Biblioteca de Medios</h1>
          <p className="text-muted-foreground font-body">
            Gestiona imágenes y videos para tus publicaciones
          </p>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,video/*"
            className="hidden"
            onChange={handleUpload}
          />
          <Button
            className="gradient-primary"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Upload className="mr-2 h-4 w-4" />
            )}
            Subir Archivo
          </Button>
        </div>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Buscar archivos..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : filtered.length === 0 ? (
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <ImageIcon className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-display font-medium mb-1">Sin archivos</h3>
            <p className="text-sm text-muted-foreground font-body">
              Sube imágenes y videos para usar en tus publicaciones
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {filtered.map((file) => {
            const isImage = file.metadata?.mimetype?.startsWith("image");
            const Icon = getFileIcon(file.metadata?.mimetype || "");
            return (
              <Card
                key={file.id}
                className="border-border/50 bg-card/80 backdrop-blur-sm overflow-hidden group"
              >
                <div className="aspect-square bg-secondary flex items-center justify-center relative">
                  {isImage ? (
                    <img
                      src={getPublicUrl(file.name)}
                      alt={file.name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <Icon className="h-12 w-12 text-muted-foreground/30" />
                  )}
                  <div className="absolute inset-0 bg-background/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive hover:text-destructive"
                      onClick={() => handleDelete(file.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardContent className="p-3">
                  <p className="text-xs font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatBytes(file.metadata?.size || 0)}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
