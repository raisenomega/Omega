import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { apiDelete } from "@/lib/api-client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { useToast } from "@/hooks/use-toast";
import { Building2, Plus, Loader2 } from "lucide-react";
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { useOnboardingForm } from "@/hooks/useOnboardingForm";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { useBusinessWizardModal } from "@/hooks/useBusinessWizardModal";
import ClientDetail from "./ClientDetail";

// Switcher V1: /clients = "Agente ARIA". ?business={id} → tabs de ClientDetail · sin activo → empty-state.
// El modal del wizard vive en useBusinessWizardModal (abrible vía ?new=1 desde el switcher). A1: editar/eliminar en tab Info.
export default function Clients() {
  const { activeBusinessId, setActiveBusiness, isReady } = useActiveBusiness();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const modal = useBusinessWizardModal();
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const wizard = useOnboardingForm({
    clientId: modal.editingClientId,
    onSuccess: (id) => {
      const wasEditing = modal.editingClientId !== null;
      modal.close();
      wizard.form.reset();
      queryClient.invalidateQueries({ queryKey: ["my_clients"] });
      queryClient.invalidateQueries({ queryKey: ["client", id] });
      if (!wasEditing) setActiveBusiness(id);
    },
  });
  // Reset híbrido (DEBT-WIZARD-RESET-DECLARATIVE): declarativo al abrir "nuevo" · síncrono al cerrar.
  useEffect(() => {
    if (modal.isOpen && modal.editingClientId === null) wizard.form.reset();
  }, [modal.isOpen, modal.editingClientId]);
  const closeWizard = () => { modal.close(); wizard.form.reset(); };
  const deleteActive = async () => {
    if (!activeBusinessId) return;
    try {
      await apiDelete(`/clients/${activeBusinessId}`);
      queryClient.invalidateQueries({ queryKey: ["my_clients"] });
      setActiveBusiness(null);
      toast({ title: "Negocio eliminado" });
    } catch (e) {
      toast({ title: "No se pudo eliminar", description: (e as Error).message, variant: "destructive" });
    }
  };
  const wizardModal = isDesktop ? (
    <Dialog open={modal.isOpen} onOpenChange={(o) => { if (!o) closeWizard(); }}>
      <DialogContent aria-describedby={undefined} className="max-w-4xl w-full h-[85vh] p-0 gap-0 border-2 border-warning">
        <DialogTitle className="sr-only">{wizard.isEditing ? "Editar negocio" : "Nuevo negocio"}</DialogTitle>
        <OnboardingWizard wizard={wizard} onClose={closeWizard} />
      </DialogContent>
    </Dialog>
  ) : (
    <Sheet open={modal.isOpen} onOpenChange={(o) => { if (!o) closeWizard(); }}>
      <SheetContent aria-describedby={undefined} side="bottom" className="h-[90vh] p-0">
        <SheetTitle className="sr-only">{wizard.isEditing ? "Editar negocio" : "Nuevo negocio"}</SheetTitle>
        <OnboardingWizard wizard={wizard} onClose={closeWizard} />
      </SheetContent>
    </Sheet>
  );
  if (!isReady) {
    return <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }
  if (activeBusinessId) {
    return (<>
      <ClientDetail clientId={activeBusinessId} onEdit={() => modal.openEdit(activeBusinessId)} onDelete={deleteActive} />
      {wizardModal}
    </>);
  }
  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-display font-bold tracking-tight">Agente ARIA</h1>
        <p className="text-sm text-muted-foreground">Activá un negocio en el header para operar su ARIA, o creá uno nuevo.</p>
      </header>
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <Building2 className="h-12 w-12 text-muted-foreground/30 mb-4" />
          <h3 className="text-lg font-medium mb-1">Sin negocio activo</h3>
          <p className="text-sm text-muted-foreground mb-4">Seleccioná un negocio en el switcher del header, o creá tu primer negocio.</p>
          <Button className="gradient-primary" onClick={modal.openNew}><Plus className="mr-2 h-4 w-4" /> Nuevo Negocio</Button>
        </CardContent>
      </Card>
      {wizardModal}
    </div>
  );
}
