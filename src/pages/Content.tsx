import { useState } from "react";
import type { Post } from "@/types/post";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import {
  FileText,
  Plus,
  Loader2,
  Send,
  Clock,
  PenLine,
  AlertCircle,
  Eye,
} from "lucide-react";

const PLATFORMS = [
  { value: "instagram", label: "Instagram", emoji: "📸" },
  { value: "facebook", label: "Facebook", emoji: "📘" },
  { value: "tiktok", label: "TikTok", emoji: "🎵" },
  { value: "twitter", label: "X / Twitter", emoji: "🐦" },
  { value: "linkedin", label: "LinkedIn", emoji: "💼" },
  { value: "youtube", label: "YouTube", emoji: "🎬" },
];

const STATUS_CONFIG: Record<string, { label: string; icon: any; color: string }> = {
  draft: { label: "Borrador", icon: PenLine, color: "bg-muted text-muted-foreground" },
  scheduled: { label: "Programado", icon: Clock, color: "bg-primary/10 text-primary" },
  published: { label: "Publicado", icon: Send, color: "bg-success/10 text-success" },
  failed: { label: "Fallido", icon: AlertCircle, color: "bg-destructive/10 text-destructive" },
};

export default function Content() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState("all");

  // Form state
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [scheduledAt, setScheduledAt] = useState("");
  const [previewContent, setPreviewContent] = useState({ title: "", body: "", platform: "" });

  // Fetch profile
  const { data: profile } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");
      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("user_id", user.id)
        .single();
      if (error) throw error;
      return data;
    },
  });

  // Fetch posts
  const { data: posts, isLoading } = useQuery<Post[]>({
    queryKey: ["posts"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("posts" as any)
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data as unknown as Post[];
    },
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!profile?.organization_id) throw new Error("No organization");
      const status = scheduledAt ? "scheduled" : "draft";
      const { error } = await (supabase.from("posts" as any) as any).insert({
        organization_id: profile.organization_id,
        title,
        body,
        platform,
        status,
        scheduled_at: scheduledAt || null,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["posts"] });
      setDialogOpen(false);
      setTitle("");
      setBody("");
      setScheduledAt("");
      toast({ title: "Publicación creada" });
    },
    onError: (e) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate();
  };

  const openPreview = (post: any) => {
    setPreviewContent({ title: post.title, body: post.body, platform: post.platform });
    setPreviewOpen(true);
  };

  const filtered = (posts ?? []).filter(
    (p) => statusFilter === "all" || p.status === statusFilter
  );

  const platformInfo = (p: string) =>
    PLATFORMS.find((pl) => pl.value === p) || { label: p, emoji: "🌐" };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold tracking-tight">Contenido</h1>
          <p className="text-muted-foreground font-body">
            Crea y gestiona publicaciones para redes sociales
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gradient-primary">
              <Plus className="mr-2 h-4 w-4" />
              Nueva Publicación
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle className="font-display">Nueva Publicación</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Título *</Label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Título de la publicación"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Contenido *</Label>
                <Textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Escribe el contenido de tu publicación..."
                  rows={5}
                  required
                />
                <p className="text-xs text-muted-foreground">{body.length} caracteres</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label>Plataforma</Label>
                  <Select value={platform} onValueChange={setPlatform}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PLATFORMS.map((p) => (
                        <SelectItem key={p.value} value={p.value}>
                          {p.emoji} {p.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Programar (opcional)</Label>
                  <Input
                    type="datetime-local"
                    value={scheduledAt}
                    onChange={(e) => setScheduledAt(e.target.value)}
                  />
                </div>
              </div>
              <Button type="submit" className="w-full gradient-primary" disabled={createMutation.isPending}>
                {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {scheduledAt ? "Programar Publicación" : "Guardar como Borrador"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filter tabs */}
      <Tabs value={statusFilter} onValueChange={setStatusFilter}>
        <TabsList>
          <TabsTrigger value="all">Todos</TabsTrigger>
          <TabsTrigger value="draft">Borradores</TabsTrigger>
          <TabsTrigger value="scheduled">Programados</TabsTrigger>
          <TabsTrigger value="published">Publicados</TabsTrigger>
          <TabsTrigger value="failed">Fallidos</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Posts list */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : filtered.length === 0 ? (
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <FileText className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="text-lg font-display font-medium mb-1">Sin publicaciones</h3>
            <p className="text-sm text-muted-foreground font-body">Crea tu primera publicación</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((post) => {
            const pInfo = platformInfo(post.platform);
            const sConfig = STATUS_CONFIG[post.status] || STATUS_CONFIG.draft;
            const StatusIcon = sConfig.icon;
            return (
              <Card
                key={post.id}
                className="border-border/50 bg-card/80 backdrop-blur-sm hover:bg-card/90 transition-colors"
              >
                <CardContent className="flex items-center gap-4 p-4">
                  <span className="text-2xl">{pInfo.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-display font-medium truncate">{post.title}</h3>
                      <Badge className={`text-xs ${sConfig.color}`}>
                        <StatusIcon className="mr-1 h-3 w-3" />
                        {sConfig.label}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground font-body mt-1 line-clamp-1">
                      {post.body}
                    </p>
                    {post.scheduled_at && (
                      <p className="text-xs text-muted-foreground mt-1">
                        <Clock className="inline h-3 w-3 mr-1" />
                        {new Date(post.scheduled_at).toLocaleString("es")}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => openPreview(post)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Preview Dialog */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-display">Vista Previa</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-lg border border-border bg-secondary p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">{platformInfo(previewContent.platform).emoji}</span>
                <span className="text-sm font-medium">{platformInfo(previewContent.platform).label}</span>
              </div>
              <h3 className="font-display font-semibold mb-2">{previewContent.title}</h3>
              <p className="text-sm text-muted-foreground font-body whitespace-pre-wrap">
                {previewContent.body}
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
