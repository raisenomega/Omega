import { Paperclip, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const MAX_REF_IMAGE_BYTES = 5 * 1024 * 1024;  // 5MB cap base64-encoded

interface Props {
  reference_image_b64?: string;
  onChange: (b64: string | undefined) => void;
}

export function PromptAttachmentControls({ reference_image_b64, onChange }: Props) {
  const { toast } = useToast();
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast({ title: "Formatos adicionales próximamente",
        description: "Por ahora solo imágenes · PDF/doc/md en sprint futuro (DEBT-CL-020)." });
      return;
    }
    if (file.size > MAX_REF_IMAGE_BYTES) { alert("Imagen >5MB · usá una más pequeña"); return; }
    const reader = new FileReader();
    reader.onload = () => onChange((reader.result as string).split(",")[1] ?? "");
    reader.readAsDataURL(file);
  };
  return (
    <>
      <label className="absolute bottom-2 left-2 cursor-pointer p-1.5 rounded hover:bg-amber-100 dark:hover:bg-amber-950/30"
        title={reference_image_b64 ? "Referencia adjunta · click para cambiar" : "Adjuntar imagen de referencia"}>
        <Paperclip className={`h-4 w-4 ${reference_image_b64 ? "text-amber-600" : "text-muted-foreground"}`} />
        <input type="file" accept="image/*" className="hidden" onChange={handleChange} />
      </label>
      {reference_image_b64 && (
        <button type="button" onClick={() => onChange(undefined)}
          className="absolute bottom-2 left-10 p-1 rounded hover:bg-red-100 dark:hover:bg-red-950/30"
          title="Quitar referencia" aria-label="Quitar referencia">
          <X className="h-3.5 w-3.5 text-red-500" />
        </button>
      )}
    </>
  );
}
