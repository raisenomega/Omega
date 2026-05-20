import { useState, KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ARIAInputBarProps {
  onSend: (content: string) => void;
  disabled: boolean;
}

export function ARIAInputBar({ onSend, disabled }: ARIAInputBarProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border p-3 flex items-end gap-2">
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKey}
        placeholder="Habla con ARIA..."
        rows={1}
        maxLength={4000}
        disabled={disabled}
        className="resize-none min-h-[36px] max-h-32"
      />
      <Button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        size="icon"
        className="h-9 w-9 shrink-0"
        aria-label="Enviar mensaje"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
