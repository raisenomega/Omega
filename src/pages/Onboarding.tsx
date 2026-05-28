// DEBT-099 · self-service onboarding · welcome → wizard → /dashboard.
// EmailVerificationGuard envuelve para casos edge en que el user llega sin verificar.
// clientId siempre existe post-signup (trigger 00006) · wizard PATCH el placeholder.
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import OnboardingWelcome from "./OnboardingWelcome";
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { EmailVerificationGuard } from "@/components/onboarding/EmailVerificationGuard";
import { useOnboardingForm } from "@/hooks/useOnboardingForm";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useToast } from "@/hooks/use-toast";

export default function Onboarding() {
  const [started, setStarted] = useState(false);
  const { clientId, loading } = useMyPlanStatus();
  const navigate = useNavigate();
  const { toast } = useToast();
  const wizard = useOnboardingForm({
    clientId: clientId ?? undefined,
    onSuccess: () => {
      toast({ title: "¡Bienvenido a OMEGA! Tu workspace está listo.", duration: 5000 });
      navigate("/dashboard", { replace: true });
    },
  });

  if (loading) return (
    <div className="flex h-screen items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  );
  if (!clientId) return (
    <div className="flex h-screen items-center justify-center text-sm text-muted-foreground">
      Cuenta sin cliente asignado · contactá soporte.
    </div>
  );

  return (
    <EmailVerificationGuard>
      {!started
        ? <OnboardingWelcome onStart={() => setStarted(true)} />
        : <div className="min-h-screen bg-background"><div className="container mx-auto max-w-4xl px-4 py-8"><OnboardingWizard wizard={wizard} /></div></div>}
    </EmailVerificationGuard>
  );
}
