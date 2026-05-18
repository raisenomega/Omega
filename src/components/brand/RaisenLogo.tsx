import { cn } from "@/lib/utils";

interface RaisenLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  as?: "span" | "a";
  href?: string;
}

const sizeClasses = {
  sm: "text-sm",
  md: "text-lg",
  lg: "text-2xl",
  xl: "text-3xl",
};

export function RaisenLogo({ size = "md", className, as = "span", href }: RaisenLogoProps) {
  const content = (
    <>
      RAISEN<span className="text-primary">.</span>
    </>
  );

  const classes = cn(
    "font-display font-bold tracking-tight text-foreground",
    sizeClasses[size],
    className
  );

  if (as === "a" && href) {
    return <a href={href} className={classes}>{content}</a>;
  }

  return <span className={classes}>{content}</span>;
}
