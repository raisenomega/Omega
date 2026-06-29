import { PostCard } from "./PostCard";
import type { CalendarPost } from "@/hooks/useCalendarData";

interface PostsListProps {
  day: string | null;
  posts: CalendarPost[];
}

// Panel lateral del día seleccionado. Desde el Commit 1 del rediseño solo orquesta el
// scroll + estados vacíos · cada tarjeta vive en <PostCard/> (extraído · reusado por Semana/Día).
export function PostsList({ day, posts }: PostsListProps) {
  if (!day) {
    return <p className="text-xs text-muted-foreground text-center py-6">Selecciona un día del calendario</p>;
  }
  if (posts.length === 0) {
    return <p className="text-xs text-muted-foreground text-center py-6">Sin posts programados</p>;
  }
  return (
    <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
      {posts.map((p) => <PostCard key={p.id} post={p} />)}
    </div>
  );
}
