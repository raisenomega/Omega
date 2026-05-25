// Arma el toast de errores de validación zod del onboarding (extraído de useOnboardingForm
// para mantenerlo <100L · cosmético). Camina el árbol de errores de react-hook-form
// juntando "campo: mensaje" de forma recursiva.
interface OnboardingErrorToast {
  title: string;
  description: string;
  variant: "destructive";
}

function collect(obj: unknown, path = "", out: string[] = []): string[] {
  if (!obj || typeof obj !== "object") return out;
  for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
    if (v && typeof v === "object" && "message" in (v as object)) {
      out.push(`${path}${k}: ${(v as { message: string }).message}`);
    } else if (v && typeof v === "object") {
      collect(v, `${path}${k}.`, out);
    }
  }
  return out;
}

export function onboardingErrorToast(errors: unknown, isEditing: boolean): OnboardingErrorToast {
  const msgs = collect(errors);
  return {
    title: isEditing ? "No se pudo guardar · campos inválidos" : "No se pudo crear · campos inválidos",
    description: msgs.slice(0, 5).join(" · ") || "Form inválido · revisá campos required",
    variant: "destructive",
  };
}
