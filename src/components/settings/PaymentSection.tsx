import { CreditCard, ShieldCheck, Settings2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useCustomerPortal } from "@/hooks/useCustomerPortal";

export function PaymentSection() {
  const portal = useCustomerPortal();
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <CreditCard className="h-4 w-4" />Método de pago
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-1">
          <Label className="text-xs">Nombre del titular</Label>
          <Input className="h-9" disabled placeholder="Como aparece en la tarjeta" />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">Número de tarjeta</Label>
          <Input className="h-9" disabled placeholder="•••• •••• •••• ••••" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label className="text-xs">Vencimiento</Label>
            <Input className="h-9" disabled placeholder="MM/AA" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">CVV</Label>
            <Input className="h-9" disabled placeholder="•••" />
          </div>
        </div>
        <Button
          variant="outline"
          className="w-full gap-2"
          onClick={() => portal.mutate()}
          disabled={portal.isPending}
        >
          <Settings2 className="h-4 w-4" />
          {portal.isPending ? "Abriendo…" : "Gestionar suscripción"}
        </Button>
        <div className="flex items-start gap-2 text-xs text-muted-foreground pt-1">
          <ShieldCheck className="h-3.5 w-3.5 shrink-0 mt-0.5" />
          <span>Tu tarjeta se usará para renovaciones automáticas del plan. Procesado con seguridad via Stripe.</span>
        </div>
      </CardContent>
    </Card>
  );
}
