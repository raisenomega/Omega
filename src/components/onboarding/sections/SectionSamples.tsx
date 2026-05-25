import { useState } from "react";
import type { UseFormReturn } from "react-hook-form";
import { Loader2, FileText, CheckCircle2, X } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { useUploadClientContext } from "@/hooks/useUploadClientContext";
import type { OnboardingForm } from "@/lib/onboarding-schema";

const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPT = ".pdf,.docx,.md,.txt";

interface Props {
  form: UseFormReturn<OnboardingForm>;
  clientId?: string | null;  // null durante creación · presente al editar
  onPendingFile?: (f: File | null) => void;  // FIX · retiene doc para subir al crear
}

export function SectionSamples({ form, clientId, onPendingFile }: Props) {
  const { toast } = useToast();
  const samples = form.watch("brand_voice_samples") ?? [];
  const text = samples.join("\n\n");
  const upload = useUploadClientContext();
  const [uploaded, setUploaded] = useState<{ filename: string; chars: number } | null>(null);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_BYTES) { toast({ title: "Archivo >5MB", variant: "destructive" }); return; }
    if (!clientId) {
      // Nuevo Cliente (sin clientId) → retener · se sube automáticamente al crear.
      onPendingFile?.(file);
      setUploaded({ filename: file.name, chars: 0 });
      toast({ title: "Documento listo", description: "Se subirá automáticamente al crear el cliente." });
      return;
    }
    upload.mutate({ clientId, file }, {
      onSuccess: (d) => { setUploaded({ filename: d.filename, chars: d.char_count }); toast({ title: "Contexto subido", description: `${d.char_count} chars extraídos · ARIA lo usará en cada generación.` }); },
      onError: (err) => toast({ title: "Upload falló", description: err.message, variant: "destructive" }),
    });
  };

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground bg-muted/40 px-3 py-2 rounded">
        Pega 3-5 ejemplos · o sube documento contexto · ARIA también aprenderá de tus aprobaciones.
      </p>
      <div className="space-y-1">
        <Label className="text-xs">Ejemplos (línea en blanco separa)</Label>
        <Textarea rows={3} value={text}
          onChange={(e) => form.setValue("brand_voice_samples", e.target.value.split(/\n\s*\n/).map(s => s.trim()).filter(Boolean))}
          placeholder="Pega aquí tus mejores posts, uno por párrafo..." className="resize-none" />
        <p className="text-xs text-muted-foreground">{samples.length} muestra(s) detectada(s)</p>
      </div>
      <div className="space-y-1">
        <Label className="text-xs">Documento contexto del cliente (PDF · DOCX · MD · TXT · max 5MB)</Label>
        <Input type="file" accept={ACCEPT} className="h-8" onChange={handleUpload} disabled={upload.isPending} />
        {upload.isPending && <p className="text-[10px] text-muted-foreground flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin" /> Extrayendo texto...</p>}
        {uploaded && (
          <p className="text-[10px] text-emerald-600 flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" /> <FileText className="h-3 w-3" />
            {uploaded.filename} · {uploaded.chars > 0 ? `${uploaded.chars.toLocaleString()} chars · ARIA lo usará permanentemente` : "se subirá al crear el cliente"}
            <button type="button" onClick={() => { setUploaded(null); onPendingFile?.(null); }} aria-label="Limpiar visual" className="ml-1"><X className="h-3 w-3" /></button>
          </p>
        )}
      </div>
    </div>
  );
}
