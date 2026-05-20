import { Pencil, Pause, Play, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PLATFORM_LABELS, PLATFORM_COLORS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

type Acc = OnboardingForm["social_accounts"][number];

interface SocialAccountListProps {
  accounts: Acc[];
  onEdit: (index: number) => void;
  onTogglePause: (index: number) => void;
  onRemove: (index: number) => void;
}

export function SocialAccountList({ accounts, onEdit, onTogglePause, onRemove }: SocialAccountListProps) {
  if (accounts.length === 0) {
    return (
      <div className="text-xs text-muted-foreground border border-dashed border-border rounded-lg p-6 text-center">
        Sin cuentas agregadas todavía
      </div>
    );
  }
  return (
    <div className="space-y-2 max-h-[520px] overflow-y-auto pr-1">
      {accounts.map((a, i) => (
        <div key={i} className={`border border-border rounded-lg p-2.5 flex items-start gap-2 ${a.is_paused ? "opacity-60" : ""}`}>
          <span
            className="h-2.5 w-2.5 rounded-full mt-1.5 shrink-0"
            style={{ background: PLATFORM_COLORS[a.platform] }}
            aria-label={a.platform}
          />
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">
              {PLATFORM_LABELS[a.platform]} <span className="text-muted-foreground">{a.username}</span>
            </div>
            <div className="text-xs text-muted-foreground flex flex-wrap gap-1.5 mt-0.5">
              {a.approx_followers != null && <span>{a.approx_followers.toLocaleString()} seg.</span>}
              {a.is_primary && <Badge variant="secondary" className="h-4 px-1 text-[10px]">Primaria</Badge>}
              {a.is_business_account && <Badge variant="secondary" className="h-4 px-1 text-[10px]">Business</Badge>}
              {a.is_paused && <Badge variant="outline" className="h-4 px-1 text-[10px]">Pausada</Badge>}
            </div>
          </div>
          <div className="flex gap-0.5 shrink-0">
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => onEdit(i)} aria-label="Editar"><Pencil className="h-3.5 w-3.5" /></Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => onTogglePause(i)} aria-label={a.is_paused ? "Reanudar" : "Pausar"}>
              {a.is_paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
            </Button>
            <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive hover:text-destructive" onClick={() => onRemove(i)} aria-label="Quitar"><Trash2 className="h-3.5 w-3.5" /></Button>
          </div>
        </div>
      ))}
    </div>
  );
}
