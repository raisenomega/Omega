import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import * as A from "@/lib/guardian/actions";
import type { GuardianUserDetail, OpenGuardianDetail } from "@/types/guardian";

type Mode = "block" | "logout" | "reset" | "resolve" | null;
const PRESETS = ["1h", "24h", "7d", "permanente"];
const LABEL: Record<string, string> = { block: "Bloquear IP", logout: "Forzar logout", reset: "Password reset", resolve: "Resolver" };

export function GuardianActionPanel({ detail, userDetail, onDone }: { detail: OpenGuardianDetail; userDetail?: GuardianUserDetail; onDone: () => void }) {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [mode, setMode] = useState<Mode>(null);
  const [reason, setReason] = useState("");
  const [ip, setIp] = useState(detail.ip ?? userDetail?.last_login?.ip_address ?? "");
  const [preset, setPreset] = useState("24h");
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const userId = detail.userId ?? userDetail?.user_id ?? null;
  const email = userDetail?.email ?? "este usuario";
  const refresh = () => ["guardian-events", "guardian-incidents", "guardian-watchlist", "guardian-user-detail"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));

  const run = async () => {
    setBusy(true);
    try {
      if (mode === "block") {
        const exp = A.expiresFromPreset(preset);
        await A.blockIp({ ip_address: ip, reason, expires_at: exp, incident_id: detail.incidentId });
        toast({ title: `IP ${ip} bloqueada`, description: exp ? `hasta ${new Date(exp).toLocaleString("es")}` : "permanente" });
      } else if (mode === "logout" && userId) {
        const r = await A.forceLogout({ user_id: userId, reason, incident_id: detail.incidentId });
        toast({ title: "Sesiones revocadas", description: `${email} · método ${r.method}` });
      } else if (mode === "reset" && userId) {
        await A.triggerPasswordReset({ user_id: userId, reason, incident_id: detail.incidentId });
        toast({ title: "Reset enviado", description: `recovery email a ${email}` });
      } else if (mode === "resolve" && detail.incidentId) {
        await A.resolveIncident({ incident_id: detail.incidentId, resolution_notes: reason });
        toast({ title: "Incidente resuelto" });
      } else { throw new Error("contexto insuficiente para la acción"); }
      refresh(); onDone();
    } catch (e) {
      toast({ variant: "destructive", title: "Acción falló", description: e instanceof Error ? e.message : "Error" });
    } finally { setBusy(false); setConfirm(false); }
  };

  const destructive = mode === "block" || mode === "logout" || mode === "reset";
  const valid = (mode === "resolve" ? reason.trim().length >= 20 : reason.trim().length > 0) && (mode !== "block" || ip.trim().length > 0);
  const confirmMsg = mode === "logout" ? `Vas a desloguear a ${email} de TODAS sus sesiones` : mode === "reset" ? `Vas a enviarle a ${email} un link de reset` : mode === "block" ? `Vas a bloquear ${ip} (${preset})` : "";

  return (
    <div className="space-y-2 rounded border border-border/40 p-2 text-xs">
      <div className="flex flex-wrap gap-1">
        {(["block", "logout", "reset", "resolve"] as Mode[]).map((m) => (
          <Button key={m} size="sm" variant={mode === m ? "default" : "outline"} disabled={busy} onClick={() => { setMode(m); setConfirm(false); setReason(""); }}>{LABEL[m as string]}</Button>
        ))}
      </div>
      {mode && (
        <div className="space-y-1">
          {mode === "block" && (
            <>
              <Input value={ip} onChange={(e) => setIp(e.target.value)} placeholder="IP" className="h-7 text-xs" />
              <div className="flex flex-wrap gap-1">{PRESETS.map((p) => <Button key={p} size="sm" variant={preset === p ? "default" : "outline"} disabled={busy} onClick={() => setPreset(p)}>{p}</Button>)}</div>
            </>
          )}
          {mode === "resolve"
            ? <Textarea value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Notas de resolución (mín 20 chars · obligatorio)" className="text-xs" />
            : <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Razón (obligatorio · audit trail)" className="h-7 text-xs" />}
          {confirm && destructive && <p className="text-amber-500">{confirmMsg} · ¿confirmás?</p>}
          <Button size="sm" disabled={busy || !valid} onClick={() => (destructive && !confirm ? setConfirm(true) : run())}>
            {busy ? <Loader2 className="h-3 w-3 animate-spin" /> : destructive && !confirm ? "Continuar" : "Ejecutar"}
          </Button>
        </div>
      )}
    </div>
  );
}
