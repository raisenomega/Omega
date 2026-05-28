import { useDemoMode, type DemoMode } from "@/hooks/useDemoMode";

// Toggle discreto de Demo Mode · SOLO visible para cliente@omega.com · simula el plan gate.
// No es una feature real del producto: estilo sutil para no confundir.
const OPTIONS: { mode: DemoMode; label: string }[] = [
  { mode: "enterprise", label: "Enterprise" },  // default · acceso total (test owner perpetuo)
  { mode: "pro", label: "PRO" },
  { mode: "basic", label: "Básico" },
];

export function DemoModeToggle() {
  const { demoMode, setDemoMode, isDemoAccount } = useDemoMode();
  if (!isDemoAccount) return null;  // invisible para cualquier otro usuario

  return (
    <div
      className="flex items-center gap-2 border-b border-border/40 px-2 py-2"
      onClick={(e) => e.stopPropagation()}  // no cierra el dropdown al togglear
    >
      <span className="text-[10px] uppercase tracking-wide text-muted-foreground/70">Vista:</span>
      <div className="flex gap-1">
        {OPTIONS.map((o) => (
          <button
            key={o.mode}
            type="button"
            onClick={() => setDemoMode(o.mode)}
            className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-colors ${
              demoMode === o.mode
                ? "bg-amber-500 text-black"
                : "bg-muted text-muted-foreground hover:bg-muted/70"
            }`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}
