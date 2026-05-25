import { useRef, useState } from "react";
import type { UseFormReturn } from "react-hook-form";
import { Upload, Loader2, FileText, CheckCircle2, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { useUploadClientContext } from "@/hooks/useUploadClientContext";
import { BUSINESS_SIZES } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { PillGroup } from "../PillGroup";

interface Props {
  form: UseFormReturn<OnboardingForm>;
  clientId?: string | null;  // DEBT-039 V2 · upload real cuando edit
}

const PLACEHOLDER = "¿Qué vendes? · ¿A quién? · ¿Qué te diferencia? · Contexto adicional...";
const SIZE_LABELS = { solo: "Solo", pequeno: "2-10", mediano: "11-50", grande: "50+" };
const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPT = ".pdf,.docx,.md,.txt";

export function SectionBusiness({ form, clientId }: Props) {
  const { toast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const upload = useUploadClientContext();
  const [uploaded, setUploaded] = useState<{ filename: string; chars: number } | null>(null);
  const v = form.watch("business");
  // BUG 1 fix · doc guardado (del GET /onboarding-data) o recién subido (estado local)
  const savedCtx = form.watch("uploaded_context");
  const shown = uploaded ?? (savedCtx ? { filename: savedCtx.filename ?? "documento", chars: savedCtx.char_count } : null);
  const set = <K extends keyof OnboardingForm["business"]>(k: K, x: OnboardingForm["business"][K]) => form.setValue(`business.${k}`, x);

  const handleFile = (f: File | undefined) => {
    if (!f) return;
    if (fileRef.current) fileRef.current.value = "";
    if (f.size > MAX_BYTES) { toast({ title: "Archivo >5MB", variant: "destructive" }); return; }
    if (!clientId) { toast({ title: "Guardá primero el cliente", description: "El upload requiere cliente creado · cerrá el wizard y editá después." }); return; }
    upload.mutate({ clientId, file: f }, {
      onSuccess: (d) => { setUploaded({ filename: d.filename, chars: d.char_count }); toast({ title: "Contexto subido", description: `${d.char_count} chars extraídos · ARIA lo usará en cada generación.` }); },
      onError: (err) => toast({ title: "Upload falló", description: err.message, variant: "destructive" }),
    });
  };

  return (
    <div className="space-y-3">
      <div className="border border-dashed border-border rounded-lg p-2 bg-muted/30 flex items-center justify-between gap-2">
        <p className="text-xs text-muted-foreground flex-1">Sube PDF · DOCX · MD · TXT (max 5MB) · ARIA lo usará permanentemente en cada generación para este cliente.</p>
        <Button size="sm" variant="outline" onClick={() => fileRef.current?.click()} disabled={upload.isPending || !clientId} className="gap-1 shrink-0 h-8">
          {upload.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />}
          {upload.isPending ? "Subiendo..." : "Subir doc"}
        </Button>
        <input ref={fileRef} type="file" accept={ACCEPT} className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
      </div>
      {!clientId && <p className="text-[10px] text-amber-600">Disponible al editar cliente (guardá primero)</p>}
      {shown && (
        <p className="text-[10px] text-emerald-600 flex items-center gap-1">
          <CheckCircle2 className="h-3 w-3" /> <FileText className="h-3 w-3" />
          {shown.filename} · {shown.chars.toLocaleString()} chars · ARIA lo usará permanentemente
          {uploaded && <button type="button" onClick={() => setUploaded(null)} aria-label="Limpiar visual" className="ml-1"><X className="h-3 w-3" /></button>}
        </p>
      )}
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Nicho</Label><Input className="h-8" value={v?.niche ?? ""} onChange={(e) => set("niche", e.target.value)} /></div>
        <div className="space-y-1"><Label className="text-xs">Vertical</Label><Input className="h-8" value={v?.vertical ?? ""} onChange={(e) => set("vertical", e.target.value)} /></div>
      </div>
      <div className="grid grid-cols-2 gap-2 items-end">
        <div className="space-y-1"><Label className="text-xs">Tamaño</Label>
          <PillGroup
            options={BUSINESS_SIZES}
            labels={SIZE_LABELS}
            value={v?.business_size ?? ""}
            onChange={(x) => set("business_size", x as OnboardingForm["business"]["business_size"])}
            cols={4}
          />
        </div>
        <div className="space-y-1"><Label className="text-xs">Años operando</Label>
          <Input className="h-8" type="number" min={0} value={v?.years_operating ?? ""} onChange={(e) => set("years_operating", e.target.value ? Number(e.target.value) : null)} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-xs">Cuéntanos sobre tu negocio</Label>
        <Textarea value={v?.business_what ?? ""} onChange={(e) => set("business_what", e.target.value)} rows={4} placeholder={PLACEHOLDER} className="resize-none" />
      </div>
    </div>
  );
}
