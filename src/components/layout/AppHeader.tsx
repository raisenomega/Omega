import { SidebarTrigger } from "@/components/ui/sidebar";
import { ARIAButton } from "@/components/aria/ARIAButton";

// DEBT-099-v2 · Bell decorativo retirado · toda notificación se consolida
// en el Card "Notificaciones" del dashboard.
export function AppHeader() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-border bg-background/80 backdrop-blur-xl px-4">
      <SidebarTrigger />
      <div className="flex-1" />
      <ARIAButton />
    </header>
  );
}
