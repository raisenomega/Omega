import { Paperclip, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const MAX_BYTES = 5 * 1024 * 1024;  // 5MB cap · texto o imagen
const ACCEPT = "image/*,.pdf,.md,.txt,.docx";

// DEBT-CL-020 cerrada: accept expandido + MIME branch.
// Image → reference_image_b64 (UX-6 · Nano Banana visual ref).
// PDF/DOCX/MD/TXT → reference_attachment_b64 + reference_mime_type (backend
// extrae texto e inyecta al system prompt o concatena al prompt según endpoint).

interface Props {
  reference_image_b64?: string;
  reference_attachment_b64?: string;
  reference_mime_type?: string;
  onImageChange: (b64: string | undefined) => void;
  onAttachmentChange: (b64: string | undefined, mime: string | undefined) => void;
}

export function PromptAttachmentControls({
  reference_image_b64, reference_attachment_b64, reference_mime_type,
  onImageChange, onAttachmentChange,
}: Props) {
  const { toast } = useToast();
  const hasAttachment = !!reference_image_b64 || !!reference_attachment_b64;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_BYTES) { toast({ title: "Archivo >5MB", description: "Usá uno más pequeño.", variant: "destructive" }); return; }
    const reader = new FileReader();
    reader.onload = () => {
      const b64 = (reader.result as string).split(",")[1] ?? "";
      if (file.type.startsWith("image/")) {
        onImageChange(b64);
        onAttachmentChange(undefined, undefined);  // mutuamente excluyentes
      } else {
        onAttachmentChange(b64, file.type || "application/octet-stream");
        onImageChange(undefined);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleRemove = () => { onImageChange(undefined); onAttachmentChange(undefined, undefined); };

  return (
    <>
      <label className="absolute bottom-2 left-2 cursor-pointer p-1.5 rounded hover:bg-amber-100 dark:hover:bg-amber-950/30"
        title={hasAttachment ? "Adjunto · click para cambiar" : "Adjuntar imagen, PDF, DOCX, MD o TXT"}>
        <Paperclip className={`h-4 w-4 ${hasAttachment ? "text-amber-600" : "text-muted-foreground"}`} />
        <input type="file" accept={ACCEPT} className="hidden" onChange={handleChange} />
      </label>
      {hasAttachment && (
        <button type="button" onClick={handleRemove}
          className="absolute bottom-2 left-10 p-1 rounded hover:bg-red-100 dark:hover:bg-red-950/30"
          title={reference_mime_type ? `Quitar adjunto (${reference_mime_type})` : "Quitar referencia"}
          aria-label="Quitar adjunto">
          <X className="h-3.5 w-3.5 text-red-500" />
        </button>
      )}
    </>
  );
}
