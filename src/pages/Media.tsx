import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";
import { MediaCard } from "@/components/media/MediaCard";
import { ImageIcon, Upload, Loader2, Search } from "lucide-react";

export default function Media() {
  useTrackOnMount("feature_open", { feature: "media" });

  const { toast } = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState("");
  const [uploading, setUploading] = useState(false);
  const { activeBusinessId, isReady } = useActiveBusiness();

  // DEBT-060: media folder-scoped por usuario (RLS {uid}/, aislamiento cross-tenant) y, dentro,
  // por negocio ({uid}/{clientId}/) para que multi-negocio del mismo dueño no comparta biblioteca.
  const { data: userId } = useQuery({
    queryKey: ["auth-user-id"],
    queryFn: async () => {
      const { data } = await supabase.auth.getUser();
      return data.user?.id ?? null;
    },
  });

  const prefix = `${userId}/${activeBusinessId}`;

  const { data: files, isLoading } = useQuery({
    queryKey: ["media-files", userId, activeBusinessId],
    queryFn: async () => {
      const { data, error } = await supabase.storage
        .from("media")
        .list(prefix, { limit: 200, sortBy: { column: "created_at", order: "desc" } });
      if (error) throw error;
      return data ?? [];
    },
    enabled: !!userId && !!activeBusinessId,
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadFiles = e.target.files;
    if (!uploadFiles || uploadFiles.length === 0) return;

    if (!userId || !activeBusinessId) {
      toast({ title: "Sesión no disponible", description: "Activá un negocio y recargá.", variant: "destructive" });
      return;
    }
    setUploading(true);
    try {
      for (const file of Array.from(uploadFiles)) {
        const fileName = `${prefix}/${Date.now()}-${file.name}`;
        const { error } = await supabase.storage
          .from("media")
          .upload(fileName, file);
        if (error) throw error;
      }
      queryClient.invalidateQueries({ queryKey: ["media-files", userId, activeBusinessId] });
      toast({ title: `${uploadFiles.length} archivo(s) subido(s)` });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error desconocido";
      toast({ title: "Error al subir", description: msg, variant: "destructive" });
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDelete = async (name: string) => {
    if (!userId || !activeBusinessId) return;
    const { error } = await supabase.storage.from("media").remove([`${prefix}/${name}`]);
    if (error) {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    } else {
      queryClient.invalidateQueries({ queryKey: ["media-files", userId, activeBusinessId] });
      toast({ title: "Archivo eliminado" });
    }
  };

  const filtered = (files ?? []).filter((f) =>
    f.name.toLowerCase().includes(search.toLowerCase())
  );

  const getPublicUrl = (name: string) =>
    supabase.storage.from("media").getPublicUrl(`${prefix}/${name}`).data.publicUrl;

  if (!isReady) return null;
  if (!activeBusinessId) return <EmptyState feature="Biblioteca de Medios" />;

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
          {filtered.map((file) => (
            <MediaCard
              key={file.id}
              file={file}
              publicUrl={getPublicUrl(file.name)}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
