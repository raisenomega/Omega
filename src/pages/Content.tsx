import { ComingSoon } from "@/components/ComingSoon";

// DEBT-033: depende de tablas `profiles` + `posts` que no existen en schema V3.
// Backend de generación de contenido es `content_lab_generated` (V3) pero el
// flow de UI requiere rewrite completo. Fase 3 §3.x.
export default function Content() {
  return (
    <ComingSoon
      title="Contenido"
      message="El módulo de generación y gestión de contenido está siendo reconstruido sobre el schema V3 (content_lab_generated). Estará disponible en la próxima versión."
    />
  );
}
