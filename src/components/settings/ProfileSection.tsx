import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { PillGroup } from "@/components/onboarding/PillGroup";
import { AvatarUpload } from "./AvatarUpload";

const PROFESSIONS = ["community_manager", "marketing_manager", "owner", "agency", "other"] as const;
const PROFESSION_LABELS: Record<string, string> = {
  community_manager: "Community Manager", marketing_manager: "Marketing Manager",
  owner: "Dueño del negocio", agency: "Agencia / Freelancer", other: "Otro",
};

export function ProfileSection() {
  const { toast } = useToast();
  const { user } = useAuth();
  const meta = (user?.user_metadata ?? {}) as { full_name?: string; role?: string; avatar_url?: string };
  const [fullName, setFullName] = useState(meta.full_name ?? "");
  const [role, setRole] = useState(meta.role ?? "");
  const [avatarUrl, setAvatarUrl] = useState(meta.avatar_url ?? "");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    const { error } = await supabase.auth.updateUser({ data: { full_name: fullName, role, avatar_url: avatarUrl } });
    setSaving(false);
    if (error) { toast({ title: "Error guardando", description: error.message, variant: "destructive" }); return; }
    toast({ title: "Perfil actualizado" });
  };

  if (!user) return null;

  return (
    <Card>
      <CardHeader><CardTitle className="text-base">Perfil del operador</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <AvatarUpload userId={user.id} fullName={fullName} email={user.email ?? ""} avatarUrl={avatarUrl} onUpload={setAvatarUrl} />
        <div className="space-y-1"><Label className="text-xs">Nombre completo</Label>
          <Input className="h-9" value={fullName} onChange={(e) => setFullName(e.target.value)} maxLength={120} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Profesión / Rol</Label>
          <PillGroup options={PROFESSIONS} labels={PROFESSION_LABELS} value={role} onChange={(x) => setRole(x as string)} cols={3} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Email</Label>
          <Input className="h-9" value={user.email ?? ""} disabled />
        </div>
        <Button onClick={handleSave} disabled={saving} className="w-full">{saving ? "Guardando…" : "Guardar"}</Button>
      </CardContent>
    </Card>
  );
}
