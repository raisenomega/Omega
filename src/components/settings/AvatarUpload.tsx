import { useRef, useState } from "react";
import { Camera, Loader2 } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

interface AvatarUploadProps {
  userId: string;
  fullName: string;
  email: string;
  avatarUrl: string;
  onUpload: (newUrl: string) => void;
}

export function AvatarUpload({ userId, fullName, email, avatarUrl, onUpload }: AvatarUploadProps) {
  const { toast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const initials = (fullName || email).split(/[ @]/).map((s) => s[0]).join("").toUpperCase().slice(0, 2) || "U";

  const handleUpload = async (f: File | undefined) => {
    if (!f) return;
    setUploading(true);
    try {
      const ext = (f.name.split(".").pop() || "png").toLowerCase();
      const path = `${userId}/avatar.${ext}`;
      const { error } = await supabase.storage.from("avatars").upload(path, f, { upsert: true, contentType: f.type });
      if (error) throw error;
      const { data } = supabase.storage.from("avatars").getPublicUrl(path);
      onUpload(`${data.publicUrl}?t=${Date.now()}`);
      toast({ title: "Foto subida" });
    } catch (e) { toast({ title: "Error subiendo foto", description: String(e), variant: "destructive" }); }
    setUploading(false);
  };

  return (
    <div className="flex items-center gap-4">
      <button type="button" onClick={() => fileRef.current?.click()} className="relative group">
        <Avatar className="h-16 w-16">
          {avatarUrl && <AvatarImage src={avatarUrl} alt={fullName} className="object-cover" />}
          <AvatarFallback className="text-base">{initials}</AvatarFallback>
        </Avatar>
        <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
          {uploading ? <Loader2 className="h-4 w-4 text-white animate-spin" /> : <Camera className="h-4 w-4 text-white" />}
        </div>
      </button>
      <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => handleUpload(e.target.files?.[0])} />
      <p className="text-xs text-muted-foreground">Click en la foto para subir una nueva.</p>
    </div>
  );
}
