// F.1 · preview swipeable de las N placas de un carrusel · reusa carousel.tsx (embla · 1er consumidor).
// Compartido entre la tarjeta (compacto, sin flechas) y el modal expandido (grande, con flechas).
// White-label: solo muestra las imágenes + el caption (título) · nunca visual_note/provider/modelo.
import {
  Carousel, CarouselContent, CarouselItem, CarouselPrevious, CarouselNext,
} from "@/components/ui/carousel";

interface Props {
  urls: string[];
  caption?: string;
  imgClassName?: string;
  showArrows?: boolean;
}

export function CarouselPreview({ urls, caption, imgClassName, showArrows = false }: Props) {
  if (urls.length === 0) return null;
  return (
    <div className="space-y-1">
      <div className="relative">
        <Carousel>
          <CarouselContent>
            {urls.map((u, i) => (
              <CarouselItem key={i}>
                <img src={u} alt={`Placa ${i + 1}`} className={imgClassName ?? "rounded-md w-full object-cover"} />
              </CarouselItem>
            ))}
          </CarouselContent>
          {showArrows && urls.length > 1 && (<><CarouselPrevious /><CarouselNext /></>)}
        </Carousel>
        <span className="absolute top-1.5 left-1.5 z-10 rounded bg-black/60 text-white text-[10px] px-1.5 py-0.5">
          {urls.length} placas
        </span>
      </div>
      {caption && <p className="text-xs line-clamp-2 whitespace-pre-wrap">{caption}</p>}
    </div>
  );
}
