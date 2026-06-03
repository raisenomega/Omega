import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";

// NOVA chat V1: estado 100% local (useState · no persiste · handoff 2b).
// El backend POST /nova/chat/ recibe el array completo y devuelve 1 assistant.
export interface NovaMessage {
  role: "user" | "assistant";
  content: string;
}

interface NovaChatResponse {
  role: string;
  content: string;
}

const STORAGE_KEY = "nova_chat_history";

export function useNovaChat() {
  const { toast } = useToast();
  const [messages, setMessages] = useState<NovaMessage[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed: unknown = JSON.parse(raw);
      return Array.isArray(parsed) ? (parsed as NovaMessage[]) : [];
    } catch {
      return [];
    }
  });

  // Persiste los últimos 50 · silently fail si localStorage lleno/bloqueado.
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
    } catch {
      // noop
    }
  }, [messages]);

  const sendMutation = useMutation({
    mutationFn: (history: NovaMessage[]): Promise<NovaChatResponse> =>
      apiPost<NovaChatResponse>("/nova/chat/", { messages: history }),
    onSuccess: (res) => {
      setMessages((prev) => [...prev, { role: "assistant", content: res.content }]);
    },
    onError: (e: unknown) => {  // fallo visible → input no queda mudo (molde useARIAChat)
      toast({
        variant: "destructive",
        title: "NOVA no pudo responder",
        description: e instanceof Error ? e.message : "Error desconocido. Reintentá.",
      });
    },
  });

  const sendMessage = (content: string) => {
    const trimmed = content.trim();
    if (!trimmed || sendMutation.isPending) return;
    const next: NovaMessage[] = [...messages, { role: "user", content: trimmed }];
    setMessages(next);
    sendMutation.mutate(next);
  };

  return {
    messages,
    isSending: sendMutation.isPending,
    sendMessage,
  };
}
