import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { INDUSTRIES, REGIONS } from "@/lib/client-constants";

interface ProfileData { id: string; name: string | null; industry: string | null; region: string | null; }

async function authFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const { data: { session } } = await supabase.auth.getSession();
  const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  return fetch(`${base}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(session ? { Authorization: `Bearer ${session.access_token}` } : {}), ...init.headers } });
}

export function ProfileSection() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const [name, setName] = useState(""); const [industry, setIndustry] = useState(""); const [region, setRegion] = useState("");

  const q = useQuery<ProfileData>({ queryKey: ["client_profile"], queryFn: async () => { const r = await authFetch("/clients/profile"); if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); } });
  useEffect(() => { if (q.data) { setName(q.data.name ?? ""); setIndustry(q.data.industry ?? ""); setRegion(q.data.region ?? ""); } }, [q.data]);

  const m = useMutation({
    mutationFn: async () => {
      const r = await authFetch("/clients/profile", { method: "PATCH", body: JSON.stringify({ name: name || null, industry: industry || null, region: region || null }) });
      if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${r.status}`); }
      return r.json();
    },
    onSuccess: () => { toast({ title: "Perfil actualizado" }); qc.invalidateQueries({ queryKey: ["client_profile"] }); },
    onError: (e: Error) => toast({ title: "No se pudo guardar", description: e.message, variant: "destructive" }),
  });

  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Perfil del negocio</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-1"><label className="text-xs text-muted-foreground">Nombre</label><Input value={name} onChange={(e) => setName(e.target.value)} disabled={q.isLoading} maxLength={120} /></div>
        <div className="space-y-1"><label className="text-xs text-muted-foreground">Industria</label>
          <Select value={industry} onValueChange={setIndustry} disabled={q.isLoading}>
            <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
            <SelectContent>{INDUSTRIES.map((v) => <SelectItem key={v} value={v}>{v}</SelectItem>)}</SelectContent>
          </Select></div>
        <div className="space-y-1"><label className="text-xs text-muted-foreground">Región</label>
          <Select value={region} onValueChange={setRegion} disabled={q.isLoading}>
            <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
            <SelectContent>{REGIONS.map((v) => <SelectItem key={v} value={v}>{v}</SelectItem>)}</SelectContent>
          </Select></div>
        <Button onClick={() => m.mutate()} disabled={m.isPending || q.isLoading} className="w-full">{m.isPending ? "Guardando…" : "Guardar cambios"}</Button>
      </CardContent>
    </Card>
  );
}
