import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";

interface ResumenStatusRowProps {
  icon: ReactNode;
  label: string;
  value: string;
  muted?: boolean;
}

export function ResumenStatusRow({ icon, label, value, muted }: ResumenStatusRowProps) {
  return (
    <Card className="border-border/50 bg-card/40">
      <CardContent className="flex items-center gap-3 py-4">
        <span className="text-amber-500/80">{icon}</span>
        <div className="min-w-0 flex-1">
          <p className="text-xs uppercase tracking-wide text-muted-foreground/60">{label}</p>
          <p className={muted ? "text-sm text-muted-foreground/70 font-body" : "text-sm text-foreground font-body"}>
            {value}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
