import { MessageSquareQuote } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface Props {
  count: number;
}

export function BrandVoiceStats({ count }: Props) {
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="flex items-center gap-4 py-6">
        <div className="rounded-full bg-primary/10 p-3">
          <MessageSquareQuote className="h-6 w-6 text-primary" />
        </div>
        <div>
          <p className="text-3xl font-display font-semibold tracking-tight">
            {count}
          </p>
          <p className="text-sm text-muted-foreground font-body">
            {count === 1 ? "post aprobado" : "posts aprobados"} alimentan tu voz
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
