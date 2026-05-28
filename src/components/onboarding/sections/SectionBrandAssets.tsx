import { useEffect, useMemo, useRef } from "react";
import type { UseFormReturn } from "react-hook-form";
import { Check, FileText, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useExistingBrandLogoUrl } from "@/hooks/useExistingBrandLogoUrl";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

type Assets = NonNullable<OnboardingForm["brand_assets"]>;

export function SectionBrandAssets({ form }: Props) {
  const { toast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const v = form.watch("brand_assets") ?? null;
  const files = v?.logo_files ?? [];
  // DEBT-086: preview thumbnails para imágenes (object URLs revocados en cleanup · sin leaks).
  const previews = useMemo(
    () => files.map((f) => (f.type.startsWith("image/") ? URL.createObjectURL(f) : null)),
    [files],
  );
  useEffect(() => () => { previews.forEach((u) => u && URL.revokeObjectURL(u)); }, [previews]);
  const existingLogo = useExistingBrandLogoUrl(v?.logo_file_id, files.length === 0);
  const set = <K extends keyof Assets>(k: K, x: Assets[K]) =>
    form.setValue("brand_assets", { ...(v ?? {}), [k]: x } as OnboardingForm["brand_assets"]);

  const handleFiles = (selected: FileList | null) => {
    if (!selected) return;
    const arr = Array.from(selected);
    if (arr.length > 3) { toast({ title: "Máximo 3 archivos", variant: "destructive" }); return; }
    set("logo_files", arr);
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2">
        {(["primary_color", "secondary_color", "accent_color"] as const).map((k) => (
          <div key={k} className="space-y-1">
            <Label className="text-xs capitalize">{k.replace("_", " ")}</Label>
            <Input type="color" value={v?.[k] ?? "#000000"} onChange={(e) => set(k, e.target.value)} className="h-8 p-1" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Font primary</Label>
          <Input className="h-8" value={v?.font_primary ?? ""} onChange={(e) => set("font_primary", e.target.value)} placeholder="ej: Inter" />
        </div>
        <div className="space-y-1"><Label className="text-xs">Font secondary</Label>
          <Input className="h-8" value={v?.font_secondary ?? ""} onChange={(e) => set("font_secondary", e.target.value)} placeholder="ej: Georgia" />
        </div>
      </div>
      <div className="space-y-1">
        <Label className="text-xs">Logo e imágenes de marca</Label>
        <p className="text-[10px] text-muted-foreground">Sube hasta 3 archivos · cualquier formato (PNG, JPG, PDF, SVG, AI...)</p>
        <Input ref={fileRef} type="file" multiple accept="*/*" className="h-8" onChange={(e) => handleFiles(e.target.files)} />
        {files.length === 0 && existingLogo.data && (
          <div className="flex items-center gap-2 text-xs text-green-600 mt-1">
            <img src={existingLogo.data} alt="logo actual" className="h-8 w-8 rounded object-cover border" />
            <span><Check className="inline h-3.5 w-3.5 mr-1" />Logo actual · haz clic en Choose Files para reemplazar</span>
          </div>
        )}
        {files.length > 0 && (
          <>
            <p className="flex items-center gap-1 text-xs text-green-600 mt-1">
              <Check className="h-3.5 w-3.5" />
              {files.length === 1 ? "Logo cargado" : `${files.length} archivos cargados`}
            </p>
            <ul className="space-y-1 mt-1">
              {files.map((f, i) => (
                <li key={i} className="flex items-center gap-2 text-xs bg-muted/40 rounded px-2 py-1">
                  {previews[i]
                    ? <img src={previews[i] as string} alt={f.name} className="h-8 w-8 rounded object-cover border" />
                    : <FileText className="h-5 w-5 text-muted-foreground shrink-0" />}
                  <span className="truncate flex-1">{f.name}</span>
                  <Check className="h-4 w-4 text-green-600 shrink-0" />
                  <Button size="icon" variant="ghost" className="h-5 w-5" onClick={() => set("logo_files", files.filter((_, j) => j !== i))}>
                    <X className="h-3 w-3" />
                  </Button>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
}
