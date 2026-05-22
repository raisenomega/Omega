import { useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchVideoStatus, type VideoJobStatus } from "@/lib/content-lab-api";

const POLL_INTERVAL_MS = 5000;

export function useVideoJobPolling(
  jobId: string | null,
  onCompleted: (videoUrl: string, jobId: string) => void,
  onFailed: (error: string) => void,
) {
  // Refs estables · evita re-runs del useEffect cuando los callbacks son inline lambdas
  // (que cambian de referencia cada render del componente padre).
  const cbRef = useRef({ onCompleted, onFailed });
  cbRef.current = { onCompleted, onFailed };

  const { data } = useQuery<VideoJobStatus>({
    queryKey: ["video-job", jobId],
    queryFn: () => fetchVideoStatus(jobId!),
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "completed" || s === "failed" ? false : POLL_INTERVAL_MS;
    },
    enabled: !!jobId,
  });

  useEffect(() => {
    if (!data || !jobId) return;
    if (data.status === "completed" && data.video_url) {
      cbRef.current.onCompleted(data.video_url, jobId);
    } else if (data.status === "failed") {
      cbRef.current.onFailed(data.error ?? "video_generation_failed");
    }
  }, [data?.status, data?.video_url, data?.error, jobId]);
}
