import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";

// DEBT-035: Bell badge con count "3" hardcoded eliminado (P1 violation).
// Cuando exista endpoint /notifications + useNotifications hook, restaurar
// con `<span>{count > 0 && count}</span>` condicional. Por ahora el botón
// es decorativo · click no hace nada todavía.
export function AppHeader() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-border bg-background/80 backdrop-blur-xl px-4">
      <SidebarTrigger />

      <div className="flex-1" />

      <Button variant="ghost" size="icon" className="h-9 w-9" aria-label="Notificaciones">
        <Bell className="h-4 w-4" />
      </Button>
    </header>
  );
}
