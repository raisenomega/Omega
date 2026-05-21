import { useState } from "react";
import { Loader2, AlertCircle, FileText } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useContentList, type ContentStatus } from "@/hooks/useContentActions";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { ContentFilters } from "@/components/content/ContentFilters";
import { ContentCard } from "@/components/content/ContentCard";

const EMPTY_TITLES: Record<ContentStatus, string> = {
  pending: "Sin contenido pendiente",
  saved: "Sin contenido guardado todavía",
  all: "Sin contenido generado",
};

export default function Content() {
  const [status, setStatus] = useState<ContentStatus>("pending");
  const [contentType, setContentType] = useState<string | null>(null);
  useTrackOnMount("feature_open", { feature: "content" });

  const q = useContentList({ status, contentType });

  return (
    <div className="container mx-auto max-w-5xl px-4 py-6 space-y-4">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Contenido</h1>
        <p className="text-sm text-muted-foreground">
          Historial de contenido generado · aprueba y programa tus posts.
        </p>
      </header>

      <ContentFilters
        status={status}
        onStatusChange={setStatus}
        contentType={contentType}
        onContentTypeChange={setContentType}
      />

      {q.isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : q.isError ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
            <AlertCircle className="h-10 w-10 text-destructive" />
            <p className="text-sm font-medium">No se pudo cargar el contenido</p>
            <Button size="sm" variant="outline" onClick={() => q.refetch()}>Reintentar</Button>
          </CardContent>
        </Card>
      ) : (q.data?.items.length ?? 0) === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
            <FileText className="h-10 w-10 text-muted-foreground/30" />
            <p className="text-sm font-medium">{EMPTY_TITLES[status]}</p>
            <p className="text-xs text-muted-foreground">El contenido aparecerá aquí cuando los agentes lo generen.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {q.data!.items.map((item) => <ContentCard key={item.id} item={item} />)}
        </div>
      )}
    </div>
  );
}
