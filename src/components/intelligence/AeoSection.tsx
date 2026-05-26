import { AlertTriangle, CheckCircle2, type LucideIcon } from "lucide-react";

type IconKind = "check" | "alert" | "none";

interface AeoSectionProps {
  title: string;
  items: string[];
  emptyText: string;
  icon?: IconKind;
}

const ICONS: Record<"check" | "alert", { Cmp: LucideIcon; className: string }> = {
  check: { Cmp: CheckCircle2, className: "text-emerald-500" },
  alert: { Cmp: AlertTriangle, className: "text-amber-500" },
};

export function AeoSection({ title, items, emptyText, icon = "none" }: AeoSectionProps) {
  const marker = icon === "none" ? null : ICONS[icon];
  return (
    <div className="space-y-1.5">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{title}</p>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground/60 font-body">{emptyText}</p>
      ) : (
        <ul className="space-y-1">
          {items.map((it, i) => (
            <li key={`${title}-${i}`} className="flex items-start gap-2 text-sm text-foreground font-body">
              {marker && <marker.Cmp className={`mt-0.5 h-4 w-4 shrink-0 ${marker.className}`} />}
              <span>{it}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
