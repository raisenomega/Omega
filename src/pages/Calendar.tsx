import { ComingSoon } from "@/components/ComingSoon";

// DEBT-033: depende de tabla `posts` que no existe en schema V3.
// Real V3 es `scheduled_posts` con cols distintas (status, scheduled_for).
// UI calendar requiere rewrite contra ese schema. Fase 3 §3.x.
export default function Calendar() {
  return (
    <ComingSoon
      title="Calendario"
      message="El calendario editorial está siendo reconstruido sobre el schema V3 (scheduled_posts). Estará disponible en la próxima versión."
    />
  );
}
