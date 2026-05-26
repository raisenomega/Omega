import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Radio, Shield, CalendarClock, Globe, Sparkles, ArrowRight, type LucideIcon } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { useWebAnalysis } from "@/hooks/useWebAnalysis";
import { useCalendarList, type CalendarPost } from "@/hooks/useCalendarData";
import { useBrandVoiceSummary } from "@/hooks/useBrandVoiceSummary";
import { useSessionReport } from "@/hooks/useSessionReport";

interface Observation {
  id: string;
  icon: LucideIcon;
  text: string;
  time?: string;
}

function currentMonthKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function nextScheduledPost(items: CalendarPost[]): CalendarPost | null {
  const now = Date.now();
  const future = items
    .filter((p) => p.status === "pending" && new Date(p.scheduled_for).getTime() >= now)
    .sort((a, b) => new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime());
  return future[0] ?? null;
}

interface Sources {
  security?: { status: string };
  nextPost: CalendarPost | null;
  webScore: number;
  webGeneratedAt: string | null;
  corpusCount: number;
}

function buildObservations(s: Sources): Observation[] {
  const out: Observation[] = [];
  // Accionables primero
  if (s.security?.status === "revisar")
    out.push({ id: "sec", icon: Shield, text: "Revisá la seguridad de tu cuenta" });
  if (s.nextPost) {
    const preview = s.nextPost.content_preview?.trim();
    const label = preview ? preview.slice(0, 60) : "contenido programado";
    out.push({ id: "post", icon: CalendarClock, text: `Post programado: ${label}`, time: s.nextPost.scheduled_for });
  }
  // Luego SEO
  if (s.webScore > 0)
    out.push({ id: "web", icon: Globe, text: `Análisis web: ${s.webScore}/100`, time: s.webGeneratedAt ?? undefined });
  // Luego brand voice (sin score inventado · honesto)
  if (s.corpusCount > 0)
    out.push({ id: "voice", icon: Sparkles, text: `ARIA aprendió de ${s.corpusCount} aprobaciones` });
  return out.slice(0, 5);
}

export function ObservationsFeed({ clientId }: { clientId: string | null }) {
  const navigate = useNavigate();
  const web = useWebAnalysis(clientId ?? "");
  const calendar = useCalendarList(currentMonthKey(), "scheduled");
  const voice = useBrandVoiceSummary();
  const session = useSessionReport();

  const items = useMemo(
    () =>
      buildObservations({
        security: session.data ? { status: session.data.status } : undefined,
        nextPost: nextScheduledPost(calendar.data?.items ?? []),
        webScore: web.query.data?.score ?? 0,
        webGeneratedAt: web.query.data?.generated_at ?? null,
        corpusCount: voice.data?.corpus_count ?? 0,
      }),
    [session.data, calendar.data, web.query.data, voice.data]
  );

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Radio className="h-5 w-5 text-primary" />
          Observaciones
        </CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <Radio className="mb-2 h-10 w-10 opacity-30" />
            <p className="text-sm">Sin observaciones por ahora</p>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((o) => (
              <div key={o.id} className="flex items-center gap-3 rounded-lg border border-border/30 bg-muted/30 p-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10">
                  <o.icon className="h-4 w-4 text-primary" />
                </div>
                <p className="flex-1 min-w-0 truncate text-sm font-medium">{o.text}</p>
                {o.time && (
                  <span className="whitespace-nowrap text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(o.time), { addSuffix: true, locale: es })}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
        <Button variant="ghost" size="sm" className="mt-3 w-full" onClick={() => navigate("/intelligence")}>
          Ir a Inteligencia
          <ArrowRight className="h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );
}
