import { Construction } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface ComingSoonProps {
  title?: string;
  message?: string;
}

export function ComingSoon({ title, message }: ComingSoonProps = {}) {
  return (
    <div className="space-y-6">
      {title && (
        <div>
          <h1 className="text-2xl font-display font-bold tracking-tight">{title}</h1>
        </div>
      )}
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center py-24 px-6 text-center">
          <Construction className="h-12 w-12 text-muted-foreground/40 mb-4" />
          <h2 className="text-xl font-display font-medium mb-2">Próximamente</h2>
          <p className="text-sm text-muted-foreground font-body max-w-md">
            {message ?? "Esta sección está en construcción y estará disponible en una próxima versión."}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
