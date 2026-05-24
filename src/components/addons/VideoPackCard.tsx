import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface VideoPackCardProps {
  name: string;
  price: string;
  bullets: string[];
  idealFor: string;
  onActivate: () => void;
  isPending?: boolean;
}

export function VideoPackCard({ name, price, bullets, idealFor, onActivate, isPending }: VideoPackCardProps) {
  return (
    <Card className="flex flex-col h-full">
      <CardContent className="flex flex-col gap-3 p-4 flex-1">
        <div className="flex items-baseline justify-between">
          <h3 className="text-base font-semibold">{name}</h3>
          <span className="text-lg font-bold">{price}</span>
        </div>
        <ul className="space-y-1.5 flex-1">
          {bullets.map((b) => (
            <li key={b} className="flex gap-2 text-xs text-muted-foreground">
              <Check className="h-3 w-3 shrink-0 mt-0.5 text-emerald-600" />
              <span>{b}</span>
            </li>
          ))}
        </ul>
        <p className="text-xs italic text-muted-foreground border-t pt-2">
          <span className="font-medium not-italic">Ideal para:</span> {idealFor}
        </p>
        <Button
          onClick={onActivate}
          disabled={isPending}
          className="w-full bg-amber-500 hover:bg-amber-600 text-white"
        >
          {isPending ? "Redirigiendo a Stripe…" : "Activar Pack"}
        </Button>
      </CardContent>
    </Card>
  );
}
