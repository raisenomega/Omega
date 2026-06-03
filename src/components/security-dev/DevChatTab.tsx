import { MessageSquare, Copy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DevPlaceholder } from "./DevPlaceholder";
import { useSecurityDev } from "@/contexts/SecurityDevContext";
import { useToast } from "@/hooks/use-toast";

export function DevChatTab() {
  const { pendingFixPrompt } = useSecurityDev();
  const { toast } = useToast();
  return (
    <div className="space-y-4">
      {pendingFixPrompt && (
        <Card className="border-violet-500/40">
          <CardHeader><CardTitle className="text-sm">Prompt de fix pendiente</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <p className="text-xs text-muted-foreground">
              Claude DEV Chat llega en Sprint 8. Mientras tanto, copiá este prompt para resolver el issue:
            </p>
            <pre className="whitespace-pre-wrap rounded bg-muted p-3 text-xs">{pendingFixPrompt}</pre>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                navigator.clipboard.writeText(pendingFixPrompt);
                toast({ title: "Prompt copiado" });
              }}
            >
              <Copy className="h-4 w-4" /><span className="ml-2">Copiar</span>
            </Button>
          </CardContent>
        </Card>
      )}
      <DevPlaceholder icon={MessageSquare} title="Claude DEV Chat" />
    </div>
  );
}
