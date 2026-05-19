import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-border bg-background/80 backdrop-blur-xl px-4">
      <SidebarTrigger />

      <div className="flex-1" />

      <Button variant="ghost" size="icon" className="relative h-9 w-9">
        <Bell className="h-4 w-4" />
        <span className="absolute -top-0.5 -right-0.5 h-3.5 w-3.5 rounded-full gradient-primary text-[9px] font-bold text-primary-foreground flex items-center justify-center">
          3
        </span>
      </Button>
    </header>
  );
}
