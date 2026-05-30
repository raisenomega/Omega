import { AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useBrandVoiceSummary } from "@/hooks/useBrandVoiceSummary";
import { BrandVoiceStats } from "@/components/brand-voice/BrandVoiceStats";
import { LatestApprovals } from "@/components/brand-voice/LatestApprovals";
import { TopKeywords } from "@/components/brand-voice/TopKeywords";
import { useProAccess } from "@/hooks/useProAccess";
import { ProFeatureGate, ProGateLoading } from "@/components/ProFeatureGate";

export default function BrandVoicePage() {
  useTrackOnMount("feature_open", { feature: "brand_voice" });
  const access = useProAccess();
  const q = useBrandVoiceSummary();

  if (access.loading) return <ProGateLoading />;
  if (!access.hasPro)
    return <ProFeatureGate feature="Brand Voice" description="Lo que ARIA aprendió sobre tu marca." clientId={access.clientId} />;

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-display font-bold tracking-tight">
          Brand Voice
        </h1>
        <p className="text-sm text-muted-foreground font-body">
          Lo que ARIA ha aprendido sobre tu marca · solo lectura.
        </p>
      </header>

      {q.isLoading && (
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </CardContent>
        </Card>
      )}

      {q.isError && (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="flex items-center gap-3 py-6">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <p className="text-sm font-body">
              No pudimos cargar tu Brand Voice · {q.error.message}
            </p>
          </CardContent>
        </Card>
      )}

      {q.data && (
        <div className="space-y-6">
          <BrandVoiceStats count={q.data.corpus_count} />
          <div className="grid gap-6 md:grid-cols-2">
            <LatestApprovals items={q.data.latest_approvals} />
            <TopKeywords items={q.data.top_keywords} />
          </div>
        </div>
      )}
    </div>
  );
}
