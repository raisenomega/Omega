import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Heart, MessageCircle, Share2, TrendingUp } from "lucide-react";

interface TopPost {
  id: string;
  title: string;
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  engagement: number;
}

const platformColors: Record<string, string> = {
  instagram: "bg-pink-500/20 text-pink-400",
  tiktok: "bg-cyan-500/20 text-cyan-400",
  facebook: "bg-blue-500/20 text-blue-400",
  twitter: "bg-sky-500/20 text-sky-400",
  linkedin: "bg-indigo-500/20 text-indigo-400",
  youtube: "bg-red-500/20 text-red-400",
};

export function TopPostsTable({ posts }: { posts: TopPost[] }) {
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-base">Mejores Publicaciones</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Título</TableHead>
              <TableHead>Plataforma</TableHead>
              <TableHead className="text-right">
                <Heart className="h-3.5 w-3.5 inline" />
              </TableHead>
              <TableHead className="text-right">
                <MessageCircle className="h-3.5 w-3.5 inline" />
              </TableHead>
              <TableHead className="text-right">
                <Share2 className="h-3.5 w-3.5 inline" />
              </TableHead>
              <TableHead className="text-right">
                <TrendingUp className="h-3.5 w-3.5 inline" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {posts.map((post) => (
              <TableRow key={post.id}>
                <TableCell className="font-medium text-sm">{post.title}</TableCell>
                <TableCell>
                  <Badge variant="secondary" className={platformColors[post.platform] ?? ""}>
                    {post.platform}
                  </Badge>
                </TableCell>
                <TableCell className="text-right tabular-nums">{post.likes.toLocaleString()}</TableCell>
                <TableCell className="text-right tabular-nums">{post.comments.toLocaleString()}</TableCell>
                <TableCell className="text-right tabular-nums">{post.shares.toLocaleString()}</TableCell>
                <TableCell className="text-right tabular-nums font-semibold text-primary">
                  {post.engagement}%
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
