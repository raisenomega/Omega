import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

type Assets = NonNullable<OnboardingForm["brand_assets"]>;

export function SectionBrandAssets({ form }: Props) {
  const v = form.watch("brand_assets") ?? null;
  const set = <K extends keyof Assets>(k: K, x: Assets[K]) =>
    form.setValue("brand_assets", { ...(v ?? {}), [k]: x } as OnboardingForm["brand_assets"]);

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground bg-muted/40 px-3 py-2 rounded">
        Colores y tipografías ahora. Logo y brand guide se suben en Configuración después.
      </p>
      <div className="grid grid-cols-3 gap-2">
        {(["primary_color", "secondary_color", "accent_color"] as const).map((k) => (
          <div key={k} className="space-y-1">
            <Label className="text-xs capitalize">{k.replace("_", " ")}</Label>
            <Input
              type="color"
              value={v?.[k] ?? "#000000"}
              onChange={(e) => set(k, e.target.value)}
              className="h-8 p-1"
            />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <Label className="text-xs">Font primary</Label>
          <Input
            className="h-8"
            value={v?.font_primary ?? ""}
            onChange={(e) => set("font_primary", e.target.value)}
            placeholder="ej: Inter, Helvetica"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Font secondary</Label>
          <Input
            className="h-8"
            value={v?.font_secondary ?? ""}
            onChange={(e) => set("font_secondary", e.target.value)}
            placeholder="ej: Georgia, serif"
          />
        </div>
      </div>
    </div>
  );
}
