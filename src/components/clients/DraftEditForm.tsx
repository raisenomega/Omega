// Editar caption + redes destino + fecha de un draft supervisado (modo edición del modal).
// Manda SOLO los campos que cambiaron (omitir = "no tocar" · scheduled_for vacío = null = borrar fecha).
// Redes = checkboxes de las cuentas conectadas (status=active) del negocio activo: al aprobar, el backend
// hace fan-out (1 scheduled_post por red marcada con su social_account_id) → cero pending sin red (sin_red).
// El value del datetime-local recorta el offset (yyyy-MM-ddTHH:mm). Caption vacío → Guardar disabled.

import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useSupervisedQueue, type SupervisedDraft } from "@/hooks/useSupervisedQueue";
import { useConnectedNetworks } from "@/hooks/useMyAccounts";
import { feedRejectsRatio } from "@/lib/feed-aspect";

function toLocalInput(iso?: string | null): string {
  // "2026-06-01T15:00:00-04:00" -> "2026-06-01T15:00" (datetime-local no acepta offset)
  return iso ? iso.slice(0, 16) : "";
}

const PLATFORM_LABEL: Record<string, string> = {
  instagram: "Instagram", facebook: "Facebook", tiktok: "TikTok",
  linkedin: "LinkedIn", twitter: "X / Twitter", youtube: "YouTube",
};

function sameSet(a: string[], b: string[]): boolean {
  return a.length === b.length && [...a].sort().join("|") === [...b].sort().join("|");
}

export function DraftEditForm({ draft, clientId, onDone }: { draft: SupervisedDraft; clientId: string; onDone: () => void }) {
  const { editDraft } = useSupervisedQueue(clientId);
  const { data: accounts = [] } = useConnectedNetworks(clientId);
  // redes conectadas (active) del negocio · dedup por platform (lowercase = casa social_accounts.platform)
  const networks = Array.from(new Set(accounts.map((a) => a.platform.toLowerCase())));

  const initialText = draft.generated_text ?? "";
  const initialDate = toLocalInput(draft.metadata?.fecha_sugerida);
  const initialPlatforms = (draft.metadata?.platforms ?? []).map((p) => p.toLowerCase());
  const [text, setText] = useState(initialText);
  const [date, setDate] = useState(initialDate);
  const [selected, setSelected] = useState<string[]>(initialPlatforms);

  const emptyCaption = text.trim() === "";
  const platformsChanged = !sameSet(selected, initialPlatforms);
  const changed = text !== initialText || date !== initialDate || platformsChanged;

  // Lee el ratio real de la imagen (naturalWidth/Height) para avisar si IG-feed la rechazaria.
  const mediaUrl = draft.media_urls?.[0] ?? null;
  const [ratio, setRatio] = useState<number | null>(null);
  useEffect(() => {
    if (!mediaUrl) { setRatio(null); return; }
    const img = new Image();
    img.onload = () => setRatio(img.naturalHeight ? img.naturalWidth / img.naturalHeight : null);
    img.onerror = () => setRatio(null);
    img.src = mediaUrl;
    return () => { img.onload = null; img.onerror = null; };
  }, [mediaUrl]);

  // Aviso INLINE persistente (no toast, no bloqueante): imagen fuera de rango de feed Y IG marcado.
  // Mismo rango que el backend (feed-aspect.ts). Reactivo a marcar/desmarcar IG y a cambiar la imagen.
  const igSelected = selected.includes("instagram");
  const feedConflict = ratio !== null && igSelected && feedRejectsRatio("instagram", ratio);

  const toggle = (p: string) =>
    setSelected((cur) => (cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p]));

  const save = () => {
    if (!changed) { onDone(); return; }  // nada cambió → solo cerrar edición (evita 400)
    const payload: { id: string; generated_text?: string; scheduled_for?: string | null; platforms?: string[] } = { id: draft.id };
    if (text !== initialText) payload.generated_text = text;
    if (date !== initialDate) payload.scheduled_for = date === "" ? null : date;
    if (platformsChanged) payload.platforms = selected;
    editDraft.mutate(payload, { onSuccess: () => onDone() });
  };

  return (
    <div className="flex flex-col gap-3 border-t border-border/20 pt-3">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={6}
        className="text-sm" placeholder="Caption + hashtags…" />

      {/* Redes destino · al aprobar se crea 1 post por red marcada (cada una con su cuenta conectada) */}
      <div className="flex flex-col gap-1.5">
        <span className="text-xs text-muted-foreground">Redes donde publicar</span>
        {networks.length === 0 ? (
          <span className="text-[11px] text-muted-foreground">
            Este negocio no tiene redes conectadas. Conectá una en el onboarding para poder agendar.
          </span>
        ) : (
          <div className="flex flex-wrap gap-3">
            {networks.map((p) => (
              <label key={p} className="flex items-center gap-1.5 text-sm">
                <input type="checkbox" checked={selected.includes(p)} onChange={() => toggle(p)}
                  className="h-3.5 w-3.5 rounded border-border/60" />
                {PLATFORM_LABEL[p] ?? p}
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Aviso INLINE persistente · imagen vertical + IG marcado · NO bloquea (las demás redes publican igual) */}
      {feedConflict && (
        <div className="flex items-start gap-2 rounded-md border border-amber-500/60 bg-amber-500/10 p-2.5 text-[11px] text-amber-200">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>
            Esta imagen es vertical{ratio ? ` (ratio ${ratio.toFixed(2)})` : ""}. El feed de Instagram la rechaza —
            usá una imagen cuadrada o 4:5, o desmarcá Instagram. Las demás redes publican igual.
          </span>
        </div>
      )}

      <label className="flex flex-col gap-1 text-xs text-muted-foreground">
        Fecha sugerida (opcional · vacío = sin agendar)
        <input type="datetime-local" value={date} onChange={(e) => setDate(e.target.value)}
          className="rounded-md border border-border/60 bg-background px-2 py-1 text-sm text-foreground" />
      </label>

      <div className="flex items-center justify-end gap-2">
        <Button size="sm" variant="ghost" onClick={onDone} disabled={editDraft.isPending}>Cancelar</Button>
        <Button size="sm" onClick={save} disabled={emptyCaption || editDraft.isPending}>
          {editDraft.isPending ? "Guardando…" : "Guardar"}
        </Button>
      </div>
    </div>
  );
}
