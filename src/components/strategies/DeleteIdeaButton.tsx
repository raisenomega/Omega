import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader, AlertDialogTitle,
  AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction,
} from "@/components/ui/alert-dialog";
import { useDeleteIdea } from "@/hooks/useDeleteIdea";

// Fase C.3 · botón "Eliminar" de una idea archivada · ⚠️ el AlertDialog de confirmación es
// OBLIGATORIO (borrado irreversible · NUNCA borra con un solo clic). Solo al confirmar → DELETE.
export function DeleteIdeaButton({ id }: { id: string }) {
  const del = useDeleteIdea();
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button size="sm" variant="ghost" className="gap-1 h-8 w-full text-muted-foreground hover:text-destructive">
          <Trash2 className="h-3.5 w-3.5" /> Eliminar
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>¿Eliminar para siempre?</AlertDialogTitle>
          <AlertDialogDescription>Esta idea se borrará de forma permanente. No se puede deshacer.</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction
            onClick={() => del.mutate({ id })}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            Eliminar
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
