import { useEffect } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useARIA } from "@/contexts/ARIAContext";
import { useARIAChat } from "@/hooks/useARIAChat";
import { trackEvent } from "@/hooks/useBehavioralTracking";
import { ARIAMessagesList } from "./ARIAMessagesList";
import { ARIAInputBar } from "./ARIAInputBar";
import { ARIAUpgradeBanner } from "./ARIAUpgradeBanner";

// Drawer derecho · 380px · full height · persistencia via ARIAContext
// Onopen → trackEvent('aria_opened') · captura behavioral_events §4.3
export function ARIADrawer() {
  const { isOpen, closeARIA } = useARIA();
  const chat = useARIAChat();

  useEffect(() => {
    if (isOpen) void trackEvent("aria_opened", { level: chat.ariaLevel });
  }, [isOpen, chat.ariaLevel]);

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && closeARIA()}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-[380px] flex flex-col p-0 gap-0"
      >
        <SheetHeader className="border-b border-border px-4 py-3">
          <SheetTitle className="flex items-center gap-2 text-base font-semibold">
            <span>ARIA</span>
            <span className="text-xs font-normal text-muted-foreground tabular-nums">
              Modelo {chat.ariaLevel}.0
            </span>
          </SheetTitle>
        </SheetHeader>

        <ARIAMessagesList messages={chat.messages} isSending={chat.isSending} />

        <ARIAUpgradeBanner currentLevel={chat.ariaLevel} />

        <ARIAInputBar
          onSend={chat.sendMessage}
          disabled={chat.isSending || chat.isLoadingHistory}
        />
      </SheetContent>
    </Sheet>
  );
}
