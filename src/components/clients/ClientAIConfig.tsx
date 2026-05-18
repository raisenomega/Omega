import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Sparkles, Zap, Crown, DollarSign, Check } from "lucide-react";

const PACKAGES = [
  {
    key: "basic",
    label: "Básico",
    icon: Zap,
    color: "text-blue-400",
    bg: "bg-blue-500/10 border-blue-500/20",
    bgActive: "bg-blue-500/20 border-blue-500/50 ring-2 ring-blue-500/30",
    description: "Lovable AI integrado · Textos e imágenes básicas",
    maxProviders: 1,
  },
  {
    key: "pro",
    label: "Pro",
    icon: Sparkles,
    color: "text-purple-400",
    bg: "bg-purple-500/10 border-purple-500/20",
    bgActive: "bg-purple-500/20 border-purple-500/50 ring-2 ring-purple-500/30",
    description: "Hasta 3 proveedores · Textos, imágenes y audio",
    maxProviders: 3,
  },
  {
    key: "enterprise",
    label: "Enterprise",
    icon: Crown,
    color: "text-amber-400",
    bg: "bg-amber-500/10 border-amber-500/20",
    bgActive: "bg-amber-500/20 border-amber-500/50 ring-2 ring-amber-500/30",
    description: "Todos los proveedores · Video, voz y contenido ilimitado",
    maxProviders: 99,
  },
] as const;

const CAPABILITY_LABELS: Record<string, { label: string; emoji: string }> = {
  text: { label: "Texto", emoji: "📝" },
  image: { label: "Imagen", emoji: "🎨" },
  video: { label: "Video", emoji: "🎬" },
  audio: { label: "Audio", emoji: "🎵" },
  voice: { label: "Voz", emoji: "🗣️" },
};

interface Props {
  clientId: string;
  organizationId: string;
}

export function ClientAIConfig({ clientId, organizationId }: Props) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: providers, isLoading: loadingProviders } = useQuery({
    queryKey: ["ai_providers"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("ai_providers")
        .select("*")
        .order("name");
      if (error) throw error;
      return data;
    },
  });

  const { data: config, isLoading: loadingConfig } = useQuery({
    queryKey: ["client_ai_config", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("client_ai_config")
        .select("*")
        .eq("client_id", clientId)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
  });

  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [selectedProviders, setSelectedProviders] = useState<string[]>([]);
  const [budget, setBudget] = useState("");

  // Sync state when data loads
  const activePackage = selectedPackage ?? config?.package ?? "basic";
  const activeProviders = selectedProviders.length > 0 ? selectedProviders : (config?.active_providers as string[] ?? ["lovable"]);
  const activeBudget = budget || (config?.monthly_budget?.toString() ?? "0");

  const currentPkgDef = PACKAGES.find((p) => p.key === activePackage)!;

  const upsertMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        client_id: clientId,
        organization_id: organizationId,
        package: activePackage,
        monthly_budget: parseFloat(activeBudget) || 0,
        active_providers: activeProviders,
      };

      if (config) {
        const { error } = await supabase
          .from("client_ai_config")
          .update(payload)
          .eq("id", config.id);
        if (error) throw error;
      } else {
        const { error } = await supabase
          .from("client_ai_config")
          .insert(payload);
        if (error) throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client_ai_config", clientId] });
      toast({ title: "Configuración AI guardada" });
    },
    onError: (e) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const toggleProvider = (slug: string) => {
    const current = [...activeProviders];
    if (current.includes(slug)) {
      if (current.length <= 1) return; // at least one
      setSelectedProviders(current.filter((s) => s !== slug));
    } else {
      if (current.length >= currentPkgDef.maxProviders) {
        toast({ title: `El paquete ${currentPkgDef.label} permite máximo ${currentPkgDef.maxProviders} proveedor(es)`, variant: "destructive" });
        return;
      }
      setSelectedProviders([...current, slug]);
    }
  };

  if (loadingProviders || loadingConfig) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Package Selection */}
      <Card className="border-border/50 bg-card/60">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Paquete AI del Cliente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PACKAGES.map((pkg) => {
              const Icon = pkg.icon;
              const isActive = activePackage === pkg.key;
              return (
                <button
                  key={pkg.key}
                  onClick={() => {
                    setSelectedPackage(pkg.key);
                    // Reset providers if switching to lower tier
                    const def = PACKAGES.find((p) => p.key === pkg.key)!;
                    if (activeProviders.length > def.maxProviders) {
                      setSelectedProviders(activeProviders.slice(0, def.maxProviders));
                    }
                  }}
                  className={`relative p-4 rounded-xl border text-left transition-all ${isActive ? pkg.bgActive : pkg.bg} hover:scale-[1.02]`}
                >
                  {isActive && (
                    <div className="absolute top-2 right-2">
                      <Check className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <Icon className={`h-6 w-6 mb-2 ${pkg.color}`} />
                  <p className="font-semibold text-sm">{pkg.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{pkg.description}</p>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Providers */}
      <Card className="border-border/50 bg-card/60">
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            Proveedores AI Activos
            <Badge variant="outline" className="text-xs">
              {activeProviders.length}/{currentPkgDef.maxProviders === 99 ? "∞" : currentPkgDef.maxProviders}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {providers?.map((provider) => {
              const isSelected = activeProviders.includes(provider.slug);
              const capabilities = (provider.capabilities as string[]) ?? [];
              return (
                <button
                  key={provider.id}
                  onClick={() => toggleProvider(provider.slug)}
                  className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-all ${
                    isSelected
                      ? "border-primary/50 bg-primary/5"
                      : "border-border/30 bg-muted/10 opacity-60 hover:opacity-100"
                  }`}
                >
                  <div className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${isSelected ? "bg-primary/20" : "bg-muted/30"}`}>
                    <Sparkles className={`h-4 w-4 ${isSelected ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{provider.name}</p>
                    <p className="text-xs text-muted-foreground line-clamp-1">{provider.description}</p>
                    <div className="flex gap-1 mt-1.5 flex-wrap">
                      {capabilities.map((cap) => (
                        <span key={cap} className="text-[10px] px-1.5 py-0.5 rounded bg-muted/40 text-muted-foreground">
                          {CAPABILITY_LABELS[cap]?.emoji} {CAPABILITY_LABELS[cap]?.label ?? cap}
                        </span>
                      ))}
                    </div>
                  </div>
                  {isSelected && <Check className="h-4 w-4 text-primary shrink-0 mt-1" />}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Budget */}
      <Card className="border-border/50 bg-card/60">
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Presupuesto Mensual
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3 max-w-sm">
            <Label className="text-sm text-muted-foreground whitespace-nowrap">USD $</Label>
            <Input
              type="number"
              min="0"
              step="10"
              value={activeBudget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="0.00"
              className="max-w-[160px]"
            />
          </div>
          {config && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>Usado: ${Number(config.budget_used ?? 0).toFixed(2)}</span>
              <span>/</span>
              <span>${Number(config.monthly_budget ?? 0).toFixed(2)}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save */}
      <div className="flex justify-end">
        <Button onClick={() => upsertMutation.mutate()} disabled={upsertMutation.isPending}>
          {upsertMutation.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
          Guardar Configuración AI
        </Button>
      </div>
    </div>
  );
}
