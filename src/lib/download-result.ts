import type { ResultV2 } from "@/components/content/ResultCardV2";

const EXT_BY_MIME: Record<string, string> = {
  "image/png": "png", "image/jpeg": "jpg", "image/webp": "webp",
  "video/mp4": "mp4", "video/webm": "webm",
};

export async function downloadResult(result: ResultV2): Promise<void> {
  const isImage = result.content_type === "image";
  const isVideo = result.content_type === "video";
  let blob: Blob;
  let ext: string;

  if (isImage || isVideo) {
    const res = await fetch(result.generated_text);
    if (!res.ok) throw new Error(`download_failed:HTTP_${res.status}`);
    blob = await res.blob();
    ext = EXT_BY_MIME[blob.type] ?? (isVideo ? "mp4" : "png");
  } else {
    blob = new Blob([result.generated_text], { type: "text/plain;charset=utf-8" });
    ext = "txt";
  }

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${result.content_type}-${result.id.slice(0, 8)}.${ext}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
