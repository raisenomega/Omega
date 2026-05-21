import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Users, Plus, Search, Mail, Phone, Building, MoreHorizontal, Pencil, Trash2, Loader2 } from "lucide-react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useNavigate } from "react-router-dom";
import { ClientSocialAccounts } from "@/components/clients/ClientSocialAccounts";
import { OnboardingWizard } from "@/components/onboarding/OnboardingWizard";
import { useOnboardingForm } from "@/hooks/useOnboardingForm";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { Sheet, SheetContent } from "@/components/ui/sheet";

export default function Clients() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [filterPlan, setFilterPlan] = useState("all");
  const [wizardOpen, setWizardOpen] = useState(false);
  const [editingClientId, setEditingClientId] = useState<string | null>(null);
  const isDesktop = useMediaQuery("(min-width: 768px)");

  // useOnboardingForm vive en el padre (NO se desmonta al cerrar Dialog/Sheet ·
  // form persiste). Cuando editingClientId !== null -> hace GET y form.reset(data).
  const wizard = useOnboardingForm({
    clientId: editingClientId,
    onSuccess: (id) => {
      const wasEditing = editingClientId !== null;
      setWizardOpen(false);
      setEditingClientId(null);
      wizard.form.reset();
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["client_onboarding_data", id] });
      if (!wasEditing) navigate(`/clients/${id}`);
    },
  });

  const { data: clients, isLoading } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("clients")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("clients").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast({ title: "Cliente eliminado" });
    },
    onError: (e) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const handleEdit = (clientId: string) => {
    setEditingClientId(clientId);
    setWizardOpen(true);
  };

  const handleClose = () => {
    setWizardOpen(false);
    setEditingClientId(null);
    wizard.form.reset();
  };

  const handleNewClient = () => {
    setEditingClientId(null);
    wizard.form.reset();
    setWizardOpen(true);
  };

  const filtered = (clients ?? []).filter((c) => {
    const matchSearch =
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.company?.toLowerCase().includes(search.toLowerCase()) ?? false) ||
      (c.email?.toLowerCase().includes(search.toLowerCase()) ?? false);
    const matchPlan = filterPlan === "all" || c.plan === filterPlan;
    return matchSearch && matchPlan;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Clientes</h1>
          <p className="text-muted-foreground">
            Gestiona tus clientes y sus cuentas sociales
          </p>
        </div>
        <Button className="gradient-primary" onClick={handleNewClient}>
          <Plus className="mr-2 h-4 w-4" />
          Nuevo Cliente
        </Button>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar clientes..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select value={filterPlan} onValueChange={setFilterPlan}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Plan" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos</SelectItem>
            <SelectItem value="basic">Básico</SelectItem>
            <SelectItem value="pro">Pro</SelectItem>
            <SelectItem value="enterprise">Enterprise</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : filtered.length === 0 ? (
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Users className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-medium mb-1">
              {clients?.length === 0 ? "Sin clientes aún" : "Sin resultados"}
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              {clients?.length === 0
                ? "Agrega tu primer cliente para empezar"
                : "Intenta con otros filtros"}
            </p>
            {clients?.length === 0 && (
              <Button className="gradient-primary" onClick={handleNewClient}>
                <Plus className="mr-2 h-4 w-4" />
                Agregar Cliente
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((client) => (
            <div key={client.id}>
              <Card
                className="border-border/50 bg-card/80 backdrop-blur-sm hover:bg-card/90 transition-colors cursor-pointer"
                onClick={() => navigate(`/clients/${client.id}`)}
              >
                <CardContent className="flex items-center gap-4 p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Users className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium truncate">{client.name}</h3>
                      <Badge variant="secondary" className="text-xs capitalize">
                        {client.plan}
                      </Badge>
                      {client.active && (
                        <div className="h-2 w-2 rounded-full bg-success" />
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                      {client.company && (
                        <span className="flex items-center gap-1">
                          <Building className="h-3 w-3" />
                          {client.company}
                        </span>
                      )}
                      {client.email && (
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {client.email}
                        </span>
                      )}
                      {client.phone && (
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          {client.phone}
                        </span>
                      )}
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(client.id);
                        }}
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        Editar
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteMutation.mutate(client.id);
                        }}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Eliminar
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      )}

      {isDesktop ? (
        <Dialog open={wizardOpen} onOpenChange={(o) => { if (!o) handleClose(); }}>
          <DialogContent className="max-w-4xl w-full h-[85vh] p-0 gap-0 border-2 border-warning">
            <OnboardingWizard wizard={wizard} onClose={handleClose} />
          </DialogContent>
        </Dialog>
      ) : (
        <Sheet open={wizardOpen} onOpenChange={(o) => { if (!o) handleClose(); }}>
          <SheetContent side="bottom" className="h-[90vh] p-0">
            <OnboardingWizard wizard={wizard} onClose={handleClose} />
          </SheetContent>
        </Sheet>
      )}
    </div>
  );
}
