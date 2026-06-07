// Selector de fotos de la Biblioteca de Medios (bucket 'media' público · {uid}/{businessId}) para
// adjuntar a un draft supervisado. Read-only del bucket · devuelve la URL pública elegida.
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { supabase } from "@/integrations/supabase/client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

export function MediaPicker({ open, onClose, onSelect }: { open: boolean; onClose: () => void; onSelect: (url: string) => void }) {
  const { activeBusinessId } = useActiveBusiness();
  const [userId, setUserId] = useState<string | null>(null);
  useEffect(() => { supabase.auth.getUser().then(({ data }) => setUserId(data.user?.id ?? null)); }, []);
  const prefix = userId && activeBusinessId ? `${userId}/${activeBusinessId}` : "";

  const { data: files, isLoading } = useQuery({
    queryKey: ["media-files", userId, activeBusinessId],
    queryFn: async () => {
      const { data, error } = await supabase.storage.from("media")
        .list(prefix, { limit: 200, sortBy: { column: "created_at", order: "desc" } });
      if (error) throw error;
      return (data ?? []).filter((f) => f.name);
    },
    enabled: open && !!prefix,
  });
  const urlOf = (name: string) => supabase.storage.from("media").getPublicUrl(`${prefix}/${name}`).data.publicUrl;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle className="text-base">Elegí una foto de tu biblioteca</DialogTitle></DialogHeader>
        {isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : !files?.length ? (
          <p className="text-xs text-muted-foreground">Tu biblioteca está vacía. Subí fotos desde Medios.</p>
        ) : (
          <div className="grid max-h-[60vh] grid-cols-3 gap-2 overflow-y-auto">
            {files.map((f) => (
              <button key={f.name} type="button" onClick={() => onSelect(urlOf(f.name))}
                className="overflow-hidden rounded-md border border-border/40 hover:border-primary">
                <img src={urlOf(f.name)} alt={f.name} loading="lazy" className="h-24 w-full object-cover" />
              </button>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
