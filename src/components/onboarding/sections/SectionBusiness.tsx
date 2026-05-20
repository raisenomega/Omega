import { useRef } from "react";
import type { UseFormReturn } from "react-hook-form";
import { Upload } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { BUSINESS_SIZES } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

const PLACEHOLDER = "¿Qué vendes?\n¿A quién le vendes?\n¿Qué te hace diferente?\nCualquier contexto adicional...";

export function SectionBusiness({ form }: Props) {
  const { toast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const v = form.watch("business");
  const set = <K extends keyof OnboardingForm["business"]>(k: K, x: OnboardingForm["business"][K]) => form.setValue(`business.${k}`, x);

  const handleFile = (f: File | undefined) => {
    if (!f) return;
    toast({ title: "Procesando...", description: "Disponible pronto · DEBT-039 · ARIA leerá tu PDF/MD" });
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="space-y-3">
      <div className="border border-dashed border-border rounded-lg p-2 bg-muted/30 flex items-center justify-between gap-2">
        <p className="text-xs text-muted-foreground flex-1">Sube PDF/MD · ARIA lo procesará automáticamente.</p>
        <Button size="sm" variant="outline" onClick={() => fileRef.current?.click()} className="gap-1 shrink-0 h-8">
          <Upload className="h-3.5 w-3.5" />PDF o .MD
        </Button>
        <input ref={fileRef} type="file" accept=".pdf,.md" className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1"><Label className="text-xs">Nicho</Label><Input className="h-8" value={v?.niche ?? ""} onChange={(e) => set("niche", e.target.value)} /></div>
        <div className="space-y-1"><Label className="text-xs">Vertical</Label><Input className="h-8" value={v?.vertical ?? ""} onChange={(e) => set("vertical", e.target.value)} /></div>
        <div className="space-y-1"><Label className="text-xs">Tamaño</Label>
          <Select value={v?.business_size ?? ""} onValueChange={(x) => set("business_size", x as OnboardingForm["business"]["business_size"])}>
            <SelectTrigger className="h-8"><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{BUSINESS_SIZES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
          </Select>
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
