// Separador estético entre secciones de Add-Ons. Línea con gradiente amber/gold que se
// desvanece en los extremos + rombo central · combina con el tema oscuro. Decorativo.
export function SectionDivider() {
  return (
    <div className="flex items-center gap-3 py-2" aria-hidden="true">
      <div className="h-px flex-1 bg-gradient-to-r from-transparent to-amber-500/40" />
      <div className="h-1.5 w-1.5 rotate-45 rounded-[1px] bg-amber-500/70 shadow-[0_0_6px_rgba(245,158,11,0.5)]" />
      <div className="h-px flex-1 bg-gradient-to-l from-transparent to-amber-500/40" />
    </div>
  );
}
