import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { KeywordCount } from "@/hooks/useBrandVoiceSummary";

interface Props {
  items: KeywordCount[];
}

export function TopKeywords({ items }: Props) {
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-base font-display">
          Tu voz en palabras
        </CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground font-body">
            Aún no hay keywords identificadas. ARIA las extrae de cada post aprobado.
          </p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {items.map((k) => (
              <Badge key={k.keyword} variant="outline" className="font-body">
                {k.keyword}
                <span className="ml-1.5 text-muted-foreground">·{k.count}</span>
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
