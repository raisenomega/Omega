import { LogOut, User as UserIcon, ChevronUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SidebarMenuButton } from "@/components/ui/sidebar";

export function SidebarUserFooter() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const fullName = user.user_metadata?.full_name as string | undefined;
  const email = user.email ?? "";
  const initials =
    fullName
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2) ||
    email[0]?.toUpperCase() ||
    "U";
  const displayName = fullName || email.split("@")[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton
          size="lg"
          className="data-[state=open]:bg-sidebar-accent group-data-[collapsible=icon]:!p-0 group-data-[collapsible=icon]:justify-center"
        >
          <Avatar className="h-8 w-8 rounded-lg shrink-0">
            <AvatarFallback className="rounded-lg gradient-primary text-xs font-bold text-primary-foreground">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
            <span className="truncate font-semibold">{displayName}</span>
            <span className="truncate text-xs text-sidebar-foreground/70">{email}</span>
          </div>
          <ChevronUp className="ml-auto h-4 w-4 group-data-[collapsible=icon]:hidden" />
        </SidebarMenuButton>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        side="top"
        sideOffset={8}
        className="w-56"
      >
        <DropdownMenuItem onClick={() => navigate("/settings")}>
          <UserIcon className="mr-2 h-4 w-4" />
          Mi Perfil
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={signOut} className="text-destructive">
          <LogOut className="mr-2 h-4 w-4" />
          Cerrar Sesión
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
