import {
  LayoutDashboard,
  Users,
  FileText,
  CalendarDays,
  BarChart3,
  Settings,
  ImageIcon,
  Mic2,
  ShieldAlert,
  Sparkles,
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
import { SidebarUserFooter } from "@/components/layout/SidebarUserFooter";

const mainItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Clientes", url: "/clients", icon: Users },
  { title: "Content Lab", url: "/content-lab", icon: Sparkles },
  { title: "Contenido", url: "/content", icon: FileText },
  { title: "Calendario", url: "/calendar", icon: CalendarDays },
  { title: "Media", url: "/media", icon: ImageIcon },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
  { title: "Brand Voice", url: "/brand-voice", icon: Mic2 },
  { title: "Crisis Room", url: "/crisis", icon: ShieldAlert },
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

      <SidebarFooter className="border-t border-sidebar-border p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarUserFooter />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
