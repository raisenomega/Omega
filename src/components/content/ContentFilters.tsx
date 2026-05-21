import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import type { ContentStatus } from "@/hooks/useContentActions";

const CONTENT_TYPES = ["text", "image", "video", "carousel"] as const;

interface ContentFiltersProps {
  status: ContentStatus;
  onStatusChange: (s: ContentStatus) => void;
  contentType: string | null;
  onContentTypeChange: (t: string | null) => void;
}

export function ContentFilters({
  status, onStatusChange, contentType, onContentTypeChange,
}: ContentFiltersProps) {
  return (
    <div className="flex items-center justify-between gap-3 flex-wrap">
      <Tabs value={status} onValueChange={(v) => onStatusChange(v as ContentStatus)}>
        <TabsList>
          <TabsTrigger value="pending">Pendientes</TabsTrigger>
          <TabsTrigger value="saved">Guardados</TabsTrigger>
          <TabsTrigger value="all">Todo</TabsTrigger>
        </TabsList>
      </Tabs>
      <div className="flex items-center gap-2">
        <Label className="text-xs text-muted-foreground">Tipo</Label>
        <Select
          value={contentType ?? "all"}
          onValueChange={(v) => onContentTypeChange(v === "all" ? null : v)}
        >
          <SelectTrigger className="h-8 w-32"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos</SelectItem>
            {CONTENT_TYPES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
