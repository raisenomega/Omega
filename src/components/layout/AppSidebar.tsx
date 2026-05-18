import {
  LayoutDashboard,
  Users,
  FileText,
  CalendarDays,
  BarChart3,
  Settings,
  ImageIcon,
} from "lucide-react";
import { RaisenLogo } from "@/components/brand/RaisenLogo";
import { RaisenCircleLogo } from "@/components/brand/RaisenCircleLogo";
import { NavLink } from "@/components/NavLink";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar";

const mainItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Clientes", url: "/clients", icon: Users },
  { title: "Contenido", url: "/content", icon: FileText },
  { title: "Calendario", url: "/calendar", icon: CalendarDays },
  { title: "Media", url: "/media", icon: ImageIcon },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
];

const configItems = [
  { title: "Configuración", url: "/settings", icon: Settings },
];

export function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-3 group-data-[collapsible=icon]:justify-center">
          <div className="flex flex-col group-data-[collapsible=icon]:hidden">
            <RaisenLogo size="md" className="text-sidebar-accent-foreground" />
            <span className="text-[10px] text-sidebar-foreground mt-0.5 uppercase tracking-widest">
              OMEGA
            </span>
          </div>
          <div className="hidden group-data-[collapsible=icon]:block">
            <RaisenCircleLogo size={32} />
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Principal</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild tooltip={item.title}>
                    <NavLink
                      to={item.url}
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    >
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Sistema</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {configItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild tooltip={item.title}>
                    <NavLink
                      to={item.url}
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    >
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-3 group-data-[collapsible=icon]:p-2">
        <div className="flex items-center gap-2 rounded-lg bg-sidebar-accent/50 p-2 group-data-[collapsible=icon]:justify-center">
          <div className="h-2 w-2 rounded-full bg-success shrink-0" />
          <span className="text-xs text-sidebar-foreground group-data-[collapsible=icon]:hidden">
            Sistema activo
          </span>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
