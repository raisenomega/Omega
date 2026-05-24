import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Sparkles, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import { apiGet, apiDelete } from "@/lib/api-client";
import { PillGroup } from "@/components/onboarding/PillGroup";

const LEVEL_INFO: Record<number, { label: string; color: string; desc: string }> = {
  1: { label: "ARIA 1.0 · Adopción", color: "bg-muted text-muted-foreground", desc: "Conversacional básico · onboarding y respuestas FAQ." },
  2: { label: "ARIA 2.0 · Básico", color: "bg-blue-500 text-white", desc: "Conversacional estándar · sugerencias + análisis simple." },
  3: { label: "ARIA 3.0 · Pro", color: "bg-emerald-500 text-white", desc: "Avanzado · NBA engine + auto-publicación con aprobación." },
  4: { label: "ARIA 4.0 · Pro+addons", color: "bg-amber-500 text-white", desc: "Near-NOVA · contexto extendido + autónomas con guardrails." },
};

// DEBT-CL-021 cerrada: api-client wrappers (fuente única auth + apiBase).
const callDeleteHistory = () => apiDelete(`/aria/history`);
const fetchAriaLevel = () => apiGet<{ aria_level: number | null }>(`/clients/profile`);

export function ARIASection() {
  const { toast } = useToast();
  const [lang, setLang] = useState<string>(() => localStorage.getItem("aria_language") || "es");
  useEffect(() => { localStorage.setItem("aria_language", lang); }, [lang]);
  const q = useQuery<{ aria_level: number | null }>({ queryKey: ["client_profile_aria"], queryFn: fetchAriaLevel });
  const level = q.data?.aria_level ?? 1;
  const info = LEVEL_INFO[level] ?? LEVEL_INFO[1];
  const onDelete = () => callDeleteHistory().then(() => toast({ title: "Historial eliminado" })).catch((e) => toast({ title: "Error", description: String(e), variant: "destructive" }));

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Sparkles className="h-4 w-4" />Tu nivel ARIA</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <Badge className={info.color}>{info.label}</Badge>
          <p className="text-xs text-muted-foreground">{info.desc}</p>
          {level < 4 && <Button disabled variant="outline" size="sm" className="w-full" title="DEBT-037 · pendiente">Subir a ARIA {level + 1}.0 · $12/mes · Próximamente</Button>}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">Idioma</CardTitle></CardHeader>
        <CardContent>
          <PillGroup options={["es", "en"] as const} labels={{ es: "Español", en: "English" }} value={lang} onChange={(x) => setLang(x as string)} cols={3} />
          <p className="text-xs text-muted-foreground mt-2">Idioma de ARIA · interfaz traducción pendiente.</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">Privacidad</CardTitle></CardHeader>
        <CardContent>
          <AlertDialog>
            <AlertDialogTrigger asChild><Button variant="outline" size="sm" className="gap-1"><Trash2 className="h-3.5 w-3.5" />Limpiar historial ARIA</Button></AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader><AlertDialogTitle>¿Limpiar historial ARIA?</AlertDialogTitle><AlertDialogDescription>Borra todas tus conversaciones con ARIA. No se puede deshacer.</AlertDialogDescription></AlertDialogHeader>
              <AlertDialogFooter><AlertDialogCancel>Cancelar</AlertDialogCancel><AlertDialogAction onClick={onDelete}>Eliminar</AlertDialogAction></AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </div>
  );
}
