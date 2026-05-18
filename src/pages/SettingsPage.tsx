import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useToast } from "@/hooks/use-toast";
import { useOrganization } from "@/hooks/useOrganization";
import {
  Settings,
  Building,
  Users,
  Shield,
  ScrollText,
  Loader2,
  Save,
} from "lucide-react";
import { format } from "date-fns";
import { es } from "date-fns/locale";

export default function SettingsPage() {
  const { toast } = useToast();
  const {
    loading,
    organization,
    team,
    auditLogs,
    updateOrg,
    updateRole,
    isAdmin,
  } = useOrganization();

  const [orgName, setOrgName] = useState("");
  const [nameInit, setNameInit] = useState(false);

  // Initialize form once data loads
  if (organization && !nameInit) {
    setOrgName(organization.name);
    setNameInit(true);
  }

  const handleSaveOrg = () => {
    if (!orgName.trim()) return;
    updateOrg.mutate(
      { name: orgName.trim() },
      {
        onSuccess: () => toast({ title: "Organización actualizada" }),
        onError: (e) =>
          toast({
            title: "Error",
            description: e.message,
            variant: "destructive",
          }),
      }
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const roleLabels: Record<string, string> = {
    admin: "Admin",
    editor: "Editor",
    viewer: "Viewer",
  };

  const roleBadgeClass: Record<string, string> = {
    admin: "bg-primary/20 text-primary border-primary/30",
    editor: "bg-chart-2/20 text-chart-2 border-chart-2/30",
    viewer: "bg-muted text-muted-foreground border-border",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-bold tracking-tight">
          Configuración
        </h1>
        <p className="text-muted-foreground">
          Administra tu organización y preferencias
        </p>
      </div>

      <Tabs defaultValue="org" className="space-y-4">
        <TabsList className="bg-secondary">
          <TabsTrigger value="org" className="gap-2">
            <Building className="h-4 w-4" />
            Organización
          </TabsTrigger>
          <TabsTrigger value="team" className="gap-2">
            <Users className="h-4 w-4" />
            Equipo
          </TabsTrigger>
          <TabsTrigger value="audit" className="gap-2">
            <ScrollText className="h-4 w-4" />
            Auditoría
          </TabsTrigger>
        </TabsList>

        {/* Organization Tab */}
        <TabsContent value="org" className="space-y-4">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Building className="h-4 w-4 text-primary" />
                Datos de la Organización
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Nombre</Label>
                <Input
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  disabled={!isAdmin}
                />
              </div>
              <div className="space-y-2">
                <Label>Slug</Label>
                <Input value={organization?.slug ?? ""} disabled />
                <p className="text-xs text-muted-foreground">
                  Identificador único (no editable)
                </p>
              </div>
              {isAdmin && (
                <Button
                  className="gradient-primary"
                  onClick={handleSaveOrg}
                  disabled={updateOrg.isPending}
                >
                  {updateOrg.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Save className="mr-2 h-4 w-4" />
                  )}
                  Guardar
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Team Tab */}
        <TabsContent value="team" className="space-y-4">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                Miembros del Equipo
              </CardTitle>
            </CardHeader>
            <CardContent>
              {team.length === 0 ? (
                <p className="text-sm text-muted-foreground py-8 text-center">
                  No hay miembros
                </p>
              ) : (
                <div className="space-y-3">
                  {team.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center gap-3 rounded-lg border border-border/50 p-3"
                    >
                      <Avatar className="h-9 w-9">
                        <AvatarFallback className="bg-primary/10 text-primary text-xs font-bold">
                          {(member.full_name || "U")
                            .split(" ")
                            .map((n: string) => n[0])
                            .join("")
                            .toUpperCase()
                            .slice(0, 2)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {member.full_name || "Sin nombre"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {member.user_id.slice(0, 8)}...
                        </p>
                      </div>
                      {isAdmin ? (
                        <Select
                          value={member.role}
                          onValueChange={(v) =>
                            updateRole.mutate(
                              { userId: member.user_id, role: v },
                              {
                                onSuccess: () =>
                                  toast({ title: "Rol actualizado" }),
                                onError: (e) =>
                                  toast({
                                    title: "Error",
                                    description: e.message,
                                    variant: "destructive",
                                  }),
                              }
                            )
                          }
                        >
                          <SelectTrigger className="w-28 h-8 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="admin">Admin</SelectItem>
                            <SelectItem value="editor">Editor</SelectItem>
                            <SelectItem value="viewer">Viewer</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <Badge
                          variant="outline"
                          className={roleBadgeClass[member.role] ?? ""}
                        >
                          {roleLabels[member.role] ?? member.role}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Tab */}
        <TabsContent value="audit" className="space-y-4">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <ScrollText className="h-4 w-4 text-primary" />
                Logs de Auditoría
              </CardTitle>
            </CardHeader>
            <CardContent>
              {auditLogs.length === 0 ? (
                <p className="text-sm text-muted-foreground py-8 text-center">
                  Sin actividad registrada aún
                </p>
              ) : (
                <div className="space-y-2">
                  {auditLogs.map((log: any) => (
                    <div
                      key={log.id}
                      className="flex items-start gap-3 rounded-lg border border-border/50 p-3 text-sm"
                    >
                      <div className="h-2 w-2 rounded-full bg-primary mt-1.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium">
                          {log.action}{" "}
                          <span className="text-muted-foreground">
                            en {log.entity_type}
                          </span>
                        </p>
                        {log.details &&
                          Object.keys(log.details).length > 0 && (
                            <p className="text-xs text-muted-foreground mt-0.5 truncate">
                              {JSON.stringify(log.details)}
                            </p>
                          )}
                      </div>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {format(new Date(log.created_at), "dd MMM HH:mm", {
                          locale: es,
                        })}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
