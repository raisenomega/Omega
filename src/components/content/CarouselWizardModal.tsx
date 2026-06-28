// F.2 · wizard 2 pasos del carrusel. Paso 1: guion editable (solo el `text` · visual_note OCULTO).
// Paso 2: render de las N placas (~10s · loading claro). On success → result carrusel a la grilla (tarjeta F.1).
// White-label: nunca muestra visual_note/provider/modelo/Zernio. Backend ya existe (NO se toca).
import { useEffect, useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useGenerateCarouselScript, type CarouselSlideData } from "@/hooks/useGenerateCarouselScript";
import { useGenerateCarouselRender } from "@/hooks/useGenerateCarouselRender";
import type { ResultV2 } from "@/components/content/result-types";

interface Props {
  open: boolean;
  idea: string;
  clientId?: string;
  tone?: string;
  onClose: () => void;
  onGenerated: (r: ResultV2) => void;
}

export function CarouselWizardModal({ open, idea, clientId, tone, onClose, onGenerated }: Props) {
  const script = useGenerateCarouselScript();
  const render = useGenerateCarouselRender();
  const [title, setTitle] = useState("");
  const [slides, setSlides] = useState<CarouselSlideData[]>([]);

  const runScript = () =>
    script.mutate({ idea, clientId, tone }, { onSuccess: (s) => { setTitle(s.carousel_title); setSlides(s.slides); } });

  // Paso 1 · al abrir genera el guion (1 vez por apertura) · al cerrar limpia el estado.
  useEffect(() => {
    if (!open) { setSlides([]); setTitle(""); script.reset(); render.reset(); return; }
    runScript();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const setText = (i: number, text: string) => setSlides((cur) => cur.map((s, j) => (j === i ? { ...s, text } : s)));
  const ready = slides.length >= 3 && title.trim() !== "" && slides.every((s) => s.text.trim() !== "");

  const generate = () =>
    render.mutate({ carouselTitle: title, slides, clientId }, {
      onSuccess: (r) => {
        onGenerated({ id: r.id, content_type: "carousel", generated_text: r.carousel_title, media_urls: r.media_urls });
        onClose();
      },
    });

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="max-w-xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Carrusel · {render.isPending ? "Paso 2/2 · generando placas" : "Paso 1/2 · revisá el guion"}</DialogTitle>
        </DialogHeader>

        {script.isPending ? (
          <div className="flex flex-col items-center gap-2 py-10">
            <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
            <p className="text-sm text-muted-foreground">ARIA está escribiendo tu guion…</p>
          </div>
        ) : script.isError ? (
          <div className="space-y-3 py-6 text-center">
            <p className="text-sm text-destructive">No se pudo generar el guion. Probá de nuevo.</p>
            <Button onClick={runScript}>Reintentar</Button>
          </div>
        ) : (
          <div className="space-y-3">
            <label className="block text-xs text-muted-foreground">Título del carrusel
              <Input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} className="mt-1" /></label>
            {slides.map((s, i) => (
              <label key={i} className="block text-xs text-muted-foreground">Placa {i + 1}
                <Textarea value={s.text} onChange={(e) => setText(i, e.target.value)} rows={2} className="mt-1 text-sm" /></label>
            ))}
            {render.isError && <p className="text-sm text-destructive">No se pudieron generar las placas. Probá de nuevo.</p>}
            <div className="flex justify-end gap-2 pt-1">
              <Button variant="ghost" onClick={onClose} disabled={render.isPending}>Cancelar</Button>
              <Button onClick={generate} disabled={!ready || render.isPending}
                className="gap-1 bg-green-600 hover:bg-green-700 text-white">
                {render.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {render.isPending ? "Generando placas… ~10s" : "Generar placas"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
