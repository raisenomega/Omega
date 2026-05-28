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
  Package,
  Brain,
  ChevronDown,
  Lock,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";
import { RaisenLogo } from "@/components/brand/RaisenLogo";
import { RaisenCircleLogo } from "@/components/brand/RaisenCircleLogo";
import { NavLink } from "@/components/NavLink";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useToast } from "@/hooks/use-toast";
import { useProAccess } from "@/hooks/useProAccess";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { useIsReseller } from "@/hooks/useIsReseller";
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

interface NavItemDef {
  title: string;
  url: string;
  icon: LucideIcon;
}

const PRINCIPAL_ITEMS: NavItemDef[] = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Clientes", url: "/clients", icon: Users },
  { title: "Content Lab", url: "/content-lab", icon: Sparkles },
  { title: "Contenido", url: "/content", icon: FileText },
  { title: "Calendario", url: "/calendar", icon: CalendarDays },
  { title: "Media", url: "/media", icon: ImageIcon },
];

const AVANZADO_ITEMS: NavItemDef[] = [
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
  { title: "Inteligencia", url: "/intelligence", icon: Brain },
  { title: "Brand Voice", url: "/brand-voice", icon: Mic2 },
  { title: "Crisis Room", url: "/crisis", icon: ShieldAlert },
];

function PlanBadge({ label, lit, color }: { label: string; lit: boolean; color: "amber" | "blue" }) {
  const litCls =
    color === "amber"
      ? "bg-amber-500/15 text-amber-500 border-amber-500/40"
      : "bg-blue-500/15 text-blue-400 border-blue-500/40";
  const cls = lit ? litCls : "bg-muted/30 text-muted-foreground/50 border-border/30";
  return (
    <span
      className={`ml-auto rounded px-1.5 py-0.5 text-[9px] font-semibold tracking-wide border ${cls} group-data-[collapsible=icon]:hidden`}
    >
      {label}
    </span>
  );
}

function NavItem({ item }: { item: NavItemDef }) {
  return (
    <SidebarMenuItem>
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
  );
}

function LockedItem({ item, onLocked }: { item: NavItemDef; onLocked: () => void }) {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton tooltip={`${item.title} · PRO`} onClick={onLocked} className="text-muted-foreground/60">
        <item.icon className="h-4 w-4" />
        <span>{item.title}</span>
        <Lock className="ml-auto h-3 w-3 group-data-[collapsible=icon]:hidden" />
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}

export function AppSidebar() {
  const { hasBasic, hasPro } = useProAccess();
  const { isSuperOwner } = useSuperOwner();
  const { isReseller } = useIsReseller();
  const { toast } = useToast();
  const lockedToast = () =>
    toast({ title: "Disponible en plan PRO", description: "Actualizá tu plan para desbloquear esta sección." });

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-3 group-data-[collapsible=icon]:justify-center">
          <div className="flex flex-col group-data-[collapsible=icon]:hidden">
            <RaisenLogo size="md" className="text-sidebar-accent-foreground" />
            <span className="text-[10px] text-sidebar-foreground mt-0.5 uppercase tracking-widest">OMEGA</span>
          </div>
          <div className="hidden group-data-[collapsible=icon]:block">
            <RaisenCircleLogo size={32} />
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="[scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {/* PRINCIPAL · colapsable · badge PRO (azul) si hasPro · si no, BÁSICO (amber) */}
        <Collapsible defaultOpen className="group/principal">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                <ChevronDown className="mr-1 h-3.5 w-3.5 transition-transform group-data-[state=closed]/principal:-rotate-90" />
                Principal
                {hasPro ? (
                  <PlanBadge label="PRO" lit color="blue" />
                ) : (
                  <PlanBadge label="BÁSICO" lit={hasBasic} color="amber" />
                )}
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {PRINCIPAL_ITEMS.map((item) => (
                    <NavItem key={item.title} item={item} />
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>

        {/* separador sutil · misma línea del fondo del sidebar */}
        <div className="mx-3 my-1 h-px bg-sidebar-border/40" />

        {/* AVANZADO · colapsable · badge PRO (azul lit si pro/ent o prueba 7d) · lock si !hasPro */}
        <Collapsible defaultOpen className="group/avanzado">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center">
                <ChevronDown className="mr-1 h-3.5 w-3.5 transition-transform group-data-[state=closed]/avanzado:-rotate-90" />
                Avanzado
                {!hasPro && !isSuperOwner && !isReseller && <PlanBadge label="PRO" lit={false} color="blue" />}
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  {AVANZADO_ITEMS.map((item) =>
                    (hasPro || isSuperOwner || isReseller) ? (
                      <NavItem key={item.title} item={item} />
                    ) : (
                      <LockedItem key={item.title} item={item} onLocked={lockedToast} />
                    ),
                  )}
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>

        {/* ADD-ONS · siempre visible (ambos planes) · punto verde */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip="Add-Ons">
                  <NavLink
                    to="/add-ons"
                    className="hover:bg-sidebar-accent/50"
                    activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                  >
                    <Package className="h-4 w-4" />
                    <span>Add-Ons</span>
                    <span className="ml-auto h-2 w-2 rounded-full bg-green-500 group-data-[collapsible=icon]:hidden" />
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* SECURITY DEV · solo is_super_owner (Ibrain · operador OMEGA) */}
        {isSuperOwner && (
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton asChild tooltip="Security Dev">
                    <NavLink
                      to="/security-dev"
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                    >
                      <ShieldCheck className="h-4 w-4" />
                      <span>Security Dev</span>
                      <span className="ml-auto h-2 w-2 rounded-full bg-violet-500 group-data-[collapsible=icon]:hidden" />
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* SISTEMA */}
        <SidebarGroup>
          <SidebarGroupLabel>Sistema</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <NavItem item={{ title: "Configuración", url: "/settings", icon: Settings }} />
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
