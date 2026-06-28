import type { ResultV2 } from "@/components/content/ResultCardV2";

const EXT_BY_MIME: Record<string, string> = {
  "image/png": "png", "image/jpeg": "jpg", "image/webp": "webp",
  "video/mp4": "mp4", "video/webm": "webm",
};

const delay = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function fetchBlob(url: string): Promise<Blob> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`download_failed:HTTP_${res.status}`);
  return res.blob();
}

// H2 · carrusel → N archivos SUELTOS (placa-1.png … placa-N.png). Delay entre cada uno: el navegador
// bloquea descargas múltiples disparadas de golpe (throttle anti-spam).
async function downloadCarousel(urls: string[]): Promise<void> {
  for (let i = 0; i < urls.length; i++) {
    const blob = await fetchBlob(urls[i]);
    const ext = EXT_BY_MIME[blob.type] ?? "png";
    triggerDownload(blob, `placa-${i + 1}.${ext}`);
    if (i < urls.length - 1) await delay(300);
  }
}

export async function downloadResult(result: ResultV2): Promise<void> {
  if (result.content_type === "carousel") return downloadCarousel(result.media_urls ?? []);

  const isImage = result.content_type === "image";
  const isVideo = result.content_type === "video";
  let blob: Blob;
  let ext: string;
  if (isImage || isVideo) {
    blob = await fetchBlob(result.generated_text);
    ext = EXT_BY_MIME[blob.type] ?? (isVideo ? "mp4" : "png");
  } else {
    blob = new Blob([result.generated_text], { type: "text/plain;charset=utf-8" });
    ext = "txt";
  }
  triggerDownload(blob, `${result.content_type}-${result.id.slice(0, 8)}.${ext}`);
}
