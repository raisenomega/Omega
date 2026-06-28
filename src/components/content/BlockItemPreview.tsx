// F.3 · thumbnail de una pieza del bloque en ScheduleModalV2 (extraído por C4 · el modal estaba en 100).
// White-label: solo media + tipo · nunca provider/modelo. El carrusel muestra la 1ª placa + cuántas placas.
import type { ResultV2 } from "./result-types";

export function BlockItemPreview({ item }: { item: ResultV2 }) {
  return (
    <div className="flex-1 min-w-0">
      <p className="text-xs font-medium capitalize">{item.content_type}</p>
      {item.content_type === "image" ? <img src={item.generated_text} alt="" className="h-16 w-16 rounded object-cover" />
        : item.content_type === "video" ? <video src={item.generated_text} className="h-16 w-16 rounded object-cover" />
        : item.content_type === "carousel" ? (
          <div className="relative h-16 w-16">
            <img src={item.media_urls?.[0]} alt="" className="h-16 w-16 rounded object-cover" />
            <span className="absolute bottom-0 right-0 rounded bg-black/60 text-white text-[9px] px-1">{item.media_urls?.length ?? 0} placas</span>
          </div>)
        : <p className="text-[10px] text-muted-foreground truncate">{item.generated_text.slice(0, 80)}</p>}
    </div>
  );
}
