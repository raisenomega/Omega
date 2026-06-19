import { useMutation, useQuery } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api-client";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";
import { platformLabel } from "@/lib/zernioConnect";

interface Page { id: string; name: string; }
interface Props {
  clientId: string;
  platform: string;
  onClose: () => void;
  onConnected: () => void;   // dispara refetch de connected-accounts en el padre · NO pinta verde acá
}

/** B-2 FB headless · page-picker. Tras el OAuth FB el callback dejó un pending (step=select_page);
 * acá listamos las páginas (pending-pages) y completamos el select. HONESTIDAD (igual que IG): el verde
 * NUNCA sale de este componente — el select devuelve {ok:true} ("Zernio aceptó"), pero el verde lo
 * deriva connected-accounts en el padre vía onConnected→refetch (verdad de Zernio). El {ok:true} solo
 * dispara el refetch, jamás pinta. Errores honestos: 409 (sesión expirada) ≠ lista vacía (0 páginas) ≠ fallo. */
export function ZernioPagePicker({ clientId, platform, onClose, onConnected }: Props) {
  const { toast } = useToast();
  const label = platformLabel(platform);
  const pages = useQuery({
    queryKey: ["zernio_pending_pages", clientId, platform],
    queryFn: () => apiGet<{ pages: Page[] }>(`/clients/${clientId}/social-accounts/${platform}/pending-pages`),
    retry: false,
  });
  const select = useMutation({
    mutationFn: (pageId: string) =>
      apiPost(`/clients/${clientId}/social-accounts/${platform}/select-page`, { page_id: pageId }),
    onSuccess: () => {
      onConnected();   // SOLO dispara la re-consulta de la verdad (connected-accounts) · el verde sale de ahí
      onClose();
      toast({ title: `Página elegida · verificando conexión de ${label}…` });   // honesto: NO afirma "conectado"
    },
    onError: (e: Error) =>
      toast({ title: "No se pudo seleccionar la página", description: e.message, variant: "destructive" }),
  });

  const expired = pages.isError && (pages.error as Error)?.message?.includes("no_pending");
  return (
    <Dialog open onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader><DialogTitle>Elegí la página de {label}</DialogTitle></DialogHeader>
        {pages.isLoading ? (
          <div className="flex justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-primary" /></div>
        ) : expired ? (
          <p className="text-sm text-muted-foreground py-4">
            La sesión de conexión expiró (15 min). Reconectá {label} desde el botón Vincular.
          </p>
        ) : pages.isError ? (
          <p className="text-sm text-destructive py-4">No se pudieron cargar las páginas. Reintentá la conexión.</p>
        ) : (pages.data?.pages.length ?? 0) === 0 ? (
          <p className="text-sm text-muted-foreground py-4">Esta cuenta no administra ninguna página de {label}.</p>
        ) : (
          <div className="space-y-2">
            {pages.data!.pages.map((p) => (
              <Button key={p.id} variant="outline" className="w-full justify-start" disabled={select.isPending}
                      onClick={() => select.mutate(p.id)}>
                {select.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}{p.name}
              </Button>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
