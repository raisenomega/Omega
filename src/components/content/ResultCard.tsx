import { Check, RefreshCw } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export interface Variation { id: string; label: string; temperature: number; generated_text: string; virality_score?: number; virality_estimated?: boolean }
export interface Result { id: string; generated_text: string; content_type: string; virality_score?: number; virality_estimated?: boolean; variations?: Variation[] }

interface Props { result: Result; onSave: (id: string) => void; onRegenerate: () => void; isSaving: boolean; isPending: boolean }

function Virality({ score, estimated }: { score?: number; estimated?: boolean }) {
  if (!score || score <= 0) return null;
  return (
    <div className="flex items-center gap-2">
      <Badge className="gap-1 bg-amber-500 text-white">🔥 {score}/100 virality</Badge>
      {estimated && <Badge variant="outline" className="text-[10px]">Estimado</Badge>}
    </div>
  );
}

function Actions({ id, onSave, onRegenerate, isSaving, isPending }: { id: string; onSave: (id: string) => void; onRegenerate: () => void; isSaving: boolean; isPending: boolean }) {
  return (
    <div className="flex gap-2">
      <Button size="sm" onClick={() => onSave(id)} disabled={isSaving} className="gap-1"><Check className="h-4 w-4" />Guardar</Button>
      <Button size="sm" variant="outline" onClick={onRegenerate} disabled={isPending} className="gap-1"><RefreshCw className="h-4 w-4" />Regenerar</Button>
    </div>
  );
}

export function ResultCard({ result, onSave, onRegenerate, isSaving, isPending }: Props) {
  const vs = result.variations ?? [];
  const isImage = result.content_type === "image";
  const isVideo = result.content_type === "video";
  const hasMulti = !isImage && !isVideo && vs.length > 1;

  return (
    <Card className="border-amber-500/30"><CardContent className="p-4 space-y-3">
      {isImage && (<>
        <img src={result.generated_text} alt="Imagen generada" className="rounded-md w-full" />
        <Actions id={result.id} onSave={onSave} onRegenerate={onRegenerate} isSaving={isSaving} isPending={isPending} />
      </>)}
      {isVideo && (<>
        <video src={result.generated_text} controls className="rounded-md w-full" />
        <Actions id={result.id} onSave={onSave} onRegenerate={onRegenerate} isSaving={isSaving} isPending={isPending} />
      </>)}
      {!isImage && !isVideo && !hasMulti && (<>
        <p className="text-sm whitespace-pre-wrap">{result.generated_text}</p>
        <Virality score={result.virality_score} estimated={result.virality_estimated} />
        <Actions id={result.id} onSave={onSave} onRegenerate={onRegenerate} isSaving={isSaving} isPending={isPending} />
      </>)}
      {hasMulti && (
        <Tabs defaultValue="A" className="w-full">
          <TabsList className="grid grid-cols-3">{vs.map(v => <TabsTrigger key={v.label} value={v.label}>{v.label} · t={v.temperature}</TabsTrigger>)}</TabsList>
          {vs.map(v => (
            <TabsContent key={v.label} value={v.label} className="space-y-3">
              <p className="text-sm whitespace-pre-wrap">{v.generated_text}</p>
              <Virality score={v.virality_score} estimated={v.virality_estimated} />
              <Actions id={v.id} onSave={onSave} onRegenerate={onRegenerate} isSaving={isSaving} isPending={isPending} />
            </TabsContent>
          ))}
        </Tabs>
      )}
    </CardContent></Card>
  );
}
