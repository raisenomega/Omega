interface SeoHeadingListProps {
  label: string;
  items: string[];
}

export function SeoHeadingList({ label, items }: SeoHeadingListProps) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground/60 font-body">
          Sin {label} detectados
        </p>
      ) : (
        <ul className="space-y-0.5">
          {items.map((t, i) => (
            <li key={`${label}-${i}`} className="text-sm text-foreground font-body">
              {t}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
