// E · picker de redes destino del bloque (fan-out multi-red). Presentacional puro: recibe las redes
// conectadas (active) ya resueltas + la selección + el toggle. Calca DraftEditForm.tsx:80-98 (modal
// Supervisado). Caso 0-redes → aviso "conectá una red primero" (guarda front del invariante).

const PLATFORM_LABEL: Record<string, string> = {
  instagram: "Instagram", facebook: "Facebook", tiktok: "TikTok",
  linkedin: "LinkedIn", twitter: "X / Twitter", youtube: "YouTube",
};

export function NetworkPicker({ networks, selected, onToggle }: {
  networks: string[];
  selected: string[];
  onToggle: (p: string) => void;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs text-muted-foreground">Redes donde publicar</span>
      {networks.length === 0 ? (
        <span className="text-[11px] text-muted-foreground">
          Este negocio no tiene redes conectadas. Conectá una en el onboarding para poder agendar.
        </span>
      ) : (
        <div className="flex flex-wrap gap-3">
          {networks.map((p) => (
            <label key={p} className="flex items-center gap-1.5 text-sm">
              <input type="checkbox" checked={selected.includes(p)} onChange={() => onToggle(p)}
                className="h-3.5 w-3.5 rounded border-border/60" />
              {PLATFORM_LABEL[p] ?? p}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
