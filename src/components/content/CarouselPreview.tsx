// F.1/H1 · preview swipeable de las N placas de un carrusel · reusa carousel.tsx (embla · 1er consumidor).
// Compartido entre la tarjeta (compacto, sin flechas) y el modal expandido (grande, flechas DENTRO + contador).
// White-label: solo muestra las imágenes + el caption (título) · nunca visual_note/provider/modelo.
import { useEffect, useState } from "react";
import {
  Carousel, CarouselContent, CarouselItem, CarouselPrevious, CarouselNext, type CarouselApi,
} from "@/components/ui/carousel";

interface Props {
  urls: string[];
  caption?: string;
  imgClassName?: string;
  showArrows?: boolean;
}

export function CarouselPreview({ urls, caption, imgClassName, showArrows = false }: Props) {
  const [api, setApi] = useState<CarouselApi>();
  const [current, setCurrent] = useState(0);
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!api) return;
    const sync = () => { setCount(api.scrollSnapList().length); setCurrent(api.selectedScrollSnap()); };
    sync();
    api.on("select", sync);
    api.on("reInit", sync);
    return () => { api.off("select", sync); api.off("reInit", sync); };
  }, [api]);

  if (urls.length === 0) return null;
  const badge = showArrows && count > 1 ? `${current + 1}/${count}` : `${urls.length} placas`;
  return (
    <div className="space-y-1">
      <div className="relative">
        <Carousel setApi={setApi}>
          <CarouselContent>
            {urls.map((u, i) => (
              <CarouselItem key={i}>
                <div className="flex items-center justify-center">
                  <img src={u} alt={`Placa ${i + 1}`} className={imgClassName ?? "rounded-md w-full object-cover"} />
                </div>
              </CarouselItem>
            ))}
          </CarouselContent>
          {showArrows && urls.length > 1 && (
            <>
              <CarouselPrevious className="left-2 top-1/2 -translate-y-1/2" />
              <CarouselNext className="right-2 top-1/2 -translate-y-1/2" />
            </>
          )}
        </Carousel>
        <span className="absolute top-1.5 left-1.5 z-10 rounded bg-black/60 text-white text-[10px] px-1.5 py-0.5">{badge}</span>
      </div>
      {caption && <p className="text-xs line-clamp-2 whitespace-pre-wrap">{caption}</p>}
    </div>
  );
}
