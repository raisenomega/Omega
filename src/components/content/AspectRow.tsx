import { ASPECTS, ASPECT_LABELS, type Aspect } from "./_aspect";

interface Props {
  aspect: Aspect;
  onChange: (a: Aspect) => void;
}

export function AspectRow({ aspect, onChange }: Props) {
  return (
    <div className="flex flex-nowrap gap-1.5 items-center justify-center">
      {ASPECTS.map(a => (
        <button key={a} type="button" onClick={() => onChange(a)}
          className={`px-2 py-1 text-[11px] rounded border ${aspect === a ? "border-amber-500 bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-300" : "border-border bg-background text-muted-foreground hover:border-muted-foreground"}`}>
          {ASPECT_LABELS[a]} {a}
        </button>
      ))}
    </div>
  );
}
