// DEBT-ARIA-UX · modal de detalle de un draft supervisado (foto + caption + hashtags).
// Honesto segun datos reales: draft con imagen (content_type=image · URL en generated_text) muestra
// la foto; draft de texto (ARIA hoy) muestra un affordance "agregar foto" VISIBLE pero no funcional
// aun (toast "pronto") — NO boton muerto, NO foto falsa. Cableado real -> sprint Media.

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ImagePlus, ImageOff, Hash } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import type { SupervisedDraft } from "@/hooks/useSupervisedQueue";

function isImageContent(d: SupervisedDraft): boolean {
  if (d.content_type === "image") return true;
  return /^https?:\/\/\S+\.(png|jpe?g|gif|webp|avif|svg)(\?\S*)?$/i.test(d.generated_text ?? "");
}

function extractHashtags(text: string): string[] {
  // Requiere al menos una letra → descarta falsos positivos numéricos: "#1" en "puesto #1", "#2024".
  return Array.from((text ?? "").matchAll(/#[\p{L}\d_]+/gu), (m) => m[0])
    .filter((t) => /\p{L}/u.test(t));
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
}

export function ClientDraftModal({ draft, onClose }: { draft: SupervisedDraft | null; onClose: () => void }) {
  const { toast } = useToast();
  const [imgFailed, setImgFailed] = useState(false);
  if (!draft) return null;

  const text = draft.generated_text ?? "";
  const tags = extractHashtags(text);
  const hasImage = isImageContent(draft) && !!text;

  return (
    <Dialog open={!!draft} onOpenChange={(o) => { if (!o) { setImgFailed(false); onClose(); } }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-base">Detalle del borrador</DialogTitle>
          <DialogDescription className="text-[11px]">
            {(draft.agent_code ?? "ARIA")} · {draft.content_type ?? "post"} · {fmtDate(draft.created_at)}
            {draft.confidence !== null ? ` · conf ${draft.confidence}` : ""}
          </DialogDescription>
        </DialogHeader>

        {/* Foto */}
        {hasImage && !imgFailed ? (
          <img src={text} alt={draft.content_type ?? "imagen"} loading="lazy"
            onError={() => setImgFailed(true)} className="rounded-md max-h-72 w-full object-cover" />
        ) : hasImage && imgFailed ? (
          <div className="flex items-center gap-2 rounded-md bg-muted/40 p-4 text-xs text-muted-foreground">
            <ImageOff className="h-4 w-4 shrink-0" /> Imagen no disponible
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 rounded-md border border-dashed border-border/60 bg-muted/10 p-6 text-center">
            <ImagePlus className="h-7 w-7 text-muted-foreground/60" />
            <p className="text-xs text-muted-foreground">Este borrador todavía no tiene foto.</p>
            <Button size="sm" variant="outline"
              onClick={() => toast({ title: "Pronto podrás agregar fotos desde tu biblioteca" })}>
              Agregar foto
            </Button>
          </div>
        )}

        {/* Caption */}
        {!hasImage && (
          <p className="text-sm whitespace-pre-wrap max-h-60 overflow-y-auto">{text || "(sin texto)"}</p>
        )}

        {/* Hashtags */}
        {tags.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 border-t border-border/20 pt-3">
            <Hash className="h-3.5 w-3.5 text-muted-foreground" />
            {tags.map((t, i) => (
              <Badge key={`${t}-${i}`} variant="secondary" className="text-[10px]">{t}</Badge>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
