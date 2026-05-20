import { CreditCard } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// DEBT-038: Stripe Customer Portal embed pendiente · Fase 3 §3.x.
// Hoy: placeholder · no expone método de pago ni invoices.
export function PaymentSection() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <CreditCard className="h-4 w-4" />Método de pago
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm text-muted-foreground">
        <p>La gestión del método de pago y descarga de facturas se realiza vía Stripe Customer Portal. Integración pendiente (DEBT-038).</p>
        <Button disabled variant="outline" className="w-full" title="DEBT-038 · pendiente Stripe Customer Portal">
          Próximamente
        </Button>
      </CardContent>
    </Card>
  );
}
