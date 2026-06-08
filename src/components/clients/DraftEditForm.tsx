// Editar caption + fecha de un draft supervisado (modo edición del modal).
// Manda SOLO los campos que cambiaron (omitir = "no tocar" en el backend · datetime-local vacío =
// scheduled_for null = borrar fecha). El value del datetime-local recorta el offset (yyyy-MM-ddTHH:mm):
// el navegador silencia un value con tz (mismo trato que ScheduleModalV2). Caption vacío → Guardar disabled.

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useSupervisedQueue, type SupervisedDraft } from "@/hooks/useSupervisedQueue";

function toLocalInput(iso?: string | null): string {
  // "2026-06-01T15:00:00-04:00" -> "2026-06-01T15:00" (datetime-local no acepta offset)
  return iso ? iso.slice(0, 16) : "";
}

export function DraftEditForm({ draft, clientId, onDone }: { draft: SupervisedDraft; clientId: string; onDone: () => void }) {
  const { editDraft } = useSupervisedQueue(clientId);
  const initialText = draft.generated_text ?? "";
  const initialDate = toLocalInput(draft.metadata?.fecha_sugerida);
  const [text, setText] = useState(initialText);
  const [date, setDate] = useState(initialDate);

  const emptyCaption = text.trim() === "";
  const changed = text !== initialText || date !== initialDate;

  const save = () => {
    if (!changed) { onDone(); return; }  // nada cambió → solo cerrar edición (evita 400)
    const payload: { id: string; generated_text?: string; scheduled_for?: string | null } = { id: draft.id };
    if (text !== initialText) payload.generated_text = text;
    if (date !== initialDate) payload.scheduled_for = date === "" ? null : date;
    editDraft.mutate(payload, { onSuccess: () => onDone() });
  };

  return (
    <div className="flex flex-col gap-3 border-t border-border/20 pt-3">
      <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={6}
        className="text-sm" placeholder="Caption + hashtags…" />
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
