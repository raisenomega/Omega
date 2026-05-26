import { Construction } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface ChipPlaceholderProps {
  title: string;
  note?: string;
}

export function ChipPlaceholder({ title, note }: ChipPlaceholderProps) {
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="flex flex-col items-center justify-center py-16 gap-3">
        <Construction className="h-10 w-10 text-muted-foreground/40" />
        <p className="text-base font-medium text-foreground">{title}</p>
        <p className="text-sm text-muted-foreground">
          {note ?? "En construcción · datos próximamente"}
        </p>
      </CardContent>
    </Card>
  );
}
