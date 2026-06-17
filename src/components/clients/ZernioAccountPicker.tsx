import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api-client";
import { autoMatch, handlesMatch, type ZernioOption } from "@/lib/zernioMatch";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Link2 } from "lucide-react";

interface Props { clientId: string; platform: string; accountName: string; currentHandle?: string | null; }

export function ZernioAccountPicker({ clientId, platform, accountName, currentHandle }: Props) {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [opts, setOpts] = useState<ZernioOption[]>([]);
  const [selected, setSelected] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  const load = async () => {
    setConfirmed(false); setSelected("");
    const r = await apiGet<{ items: ZernioOption[] }>(
      `/clients/${clientId}/zernio-available-accounts?platform=${platform}`);
    setOpts(r.items);
    setSelected(autoMatch(r.items, accountName)?.zernio_account_id ?? "");
  };

  const sel = opts.find((o) => o.zernio_account_id === selected);
  const mismatch = !!sel && !handlesMatch(sel.handle, accountName);

  const save = useMutation({
    mutationFn: () => apiPost(`/clients/${clientId}/social-accounts/${platform}/zernio`, { zernio_account_id: selected }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["social_accounts", clientId] });
      setOpen(false); toast({ title: "Cuenta Zernio vinculada" });
    },
    onError: (e: Error) => toast({ title: "Error al vincular", description: e.message, variant: "destructive" }),
  });

  return (
    <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (o) void load(); }}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="h-7 text-xs">
          <Link2 className="mr-1 h-3 w-3" />{currentHandle ? `Zernio: ${currentHandle}` : "Vincular Zernio"}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader><DialogTitle className="text-sm">Vincular Zernio · {accountName} ({platform})</DialogTitle></DialogHeader>
        <Select value={selected} onValueChange={(v) => { setSelected(v); setConfirmed(false); }}>
          <SelectTrigger><SelectValue placeholder="Elegí la cuenta de Zernio" /></SelectTrigger>
          <SelectContent>
            {opts.map((o) => (
              <SelectItem key={o.zernio_account_id} value={o.zernio_account_id}>{o.handle ?? o.zernio_account_id}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {mismatch && (
          <label className="flex items-start gap-2 rounded border border-destructive/50 bg-destructive/10 p-2 text-xs">
            <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="mt-0.5" />
            <span>Estás mapeando <b>{sel?.handle}</b> a <b>{accountName}</b> — no coinciden. Confirmo que es correcto.</span>
          </label>
        )}
        <Button className="w-full gradient-primary" disabled={!selected || (mismatch && !confirmed) || save.isPending}
                onClick={() => save.mutate()}>
          {save.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Vincular
        </Button>
      </DialogContent>
    </Dialog>
  );
}
