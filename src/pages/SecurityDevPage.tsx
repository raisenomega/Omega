import { Navigate } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { SentinelTab } from "@/components/security-dev/SentinelTab";
import { GuardianTab } from "@/components/security-dev/GuardianTab";
import { DevChatTab } from "@/components/security-dev/DevChatTab";
import { DevTerminalTab } from "@/components/security-dev/DevTerminalTab";

export default function SecurityDevPage() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return (
    <div className="space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-display font-bold tracking-tight">Security Dev</h1>
        <p className="text-sm text-muted-foreground">Panel de operador · solo visible para Ibrain</p>
      </header>
      <Tabs defaultValue="sentinel">
        <TabsList>
          <TabsTrigger value="sentinel">SENTINEL</TabsTrigger>
          <TabsTrigger value="guardian">GUARDIAN</TabsTrigger>
          <TabsTrigger value="chat">Dev Chat</TabsTrigger>
          <TabsTrigger value="terminal">Dev Terminal</TabsTrigger>
        </TabsList>
        <TabsContent value="sentinel"><SentinelTab /></TabsContent>
        <TabsContent value="guardian"><GuardianTab /></TabsContent>
        <TabsContent value="chat"><DevChatTab /></TabsContent>
        <TabsContent value="terminal"><DevTerminalTab /></TabsContent>
      </Tabs>
    </div>
  );
}
