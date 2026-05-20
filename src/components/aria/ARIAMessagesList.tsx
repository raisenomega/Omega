import { useEffect, useRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ARIAMessage } from "@/hooks/useARIAChat";

interface ARIAMessagesListProps {
  messages: ARIAMessage[];
  isSending: boolean;
}

export function ARIAMessagesList({ messages, isSending }: ARIAMessagesListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isSending]);

  if (messages.length === 0 && !isSending) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 text-center text-sm text-muted-foreground">
        Hola, soy ARIA. ¿En qué te ayudo hoy?
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {messages.map((m, i) => (
        <div
          key={`${m.created_at ?? i}-${i}`}
          className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}
        >
          <div
            className={cn(
              "max-w-[85%] rounded-lg px-3 py-2 text-sm",
              m.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-foreground",
            )}
          >
            {m.content}
          </div>
        </div>
      ))}
      {isSending && (
        <div className="flex justify-start">
          <div className="rounded-lg bg-muted px-3 py-2 text-sm">
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
