import { useEffect, useRef, useState, KeyboardEvent } from "react";
import { Loader2, Send, Crown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useNovaChat } from "@/hooks/useNovaChat";

// Edge-to-edge: -m-6 anula el p-6 del AppLayout · h-[calc(100%+3rem)] recupera
// la altura de ese padding para que la barra de input quede flush al borde inferior.
export function NovaChat() {
  const { messages, isSending, sendMessage } = useNovaChat();
  const [value, setValue] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isSending]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isSending) return;
    sendMessage(trimmed);
    setValue("");
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col -m-6 h-[calc(100%+3rem)]">
      <header className="flex items-center gap-2 border-b border-border px-4 py-3">
        <Crown className="h-5 w-5 text-amber-500" />
        <h1 className="text-lg font-display font-bold tracking-tight">NOVA</h1>
        <span className="text-xs text-muted-foreground">CEO Agent · solo operador OMEGA</span>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && !isSending ? (
          <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
            NOVA — CEO Agent. Empezá la conversación.
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}>
              <div
                className={cn(
                  "max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm",
                  m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
                )}
              >
                {m.content}
              </div>
            </div>
          ))
        )}
        {isSending && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              NOVA está pensando…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex items-end gap-2 border-t border-border p-3">
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Escribile a NOVA..."
          rows={1}
          maxLength={4000}
          disabled={isSending}
          className="min-h-[36px] max-h-32 resize-none"
        />
        <Button
          onClick={handleSend}
          disabled={isSending || !value.trim()}
          size="icon"
          className="h-9 w-9 shrink-0"
          aria-label="Enviar mensaje"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
