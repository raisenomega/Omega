import { cn } from "@/lib/utils";

interface RaisenCircleLogoProps {
  size?: number;
  className?: string;
}

export function RaisenCircleLogo({ size = 40, className }: RaisenCircleLogoProps) {
  const fontSize = size * 0.35;
  return (
    <div
      className={cn(
        "rounded-full flex items-center justify-center font-display font-bold text-foreground border-2 border-primary/60 bg-background shrink-0",
        className
      )}
      style={{ width: size, height: size, fontSize }}
    >
      R<span className="text-primary">.</span>
    </div>
  );
}
