import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { TONES, EMOJI_USAGE, HASHTAG_STRATEGY, CONTENT_FORMATS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { PillGroup } from "../PillGroup";

interface Props { form: UseFormReturn<OnboardingForm> }

const EMOJI_LABELS = { never: "Nunca", rarely: "Poco", balanced: "Balanceado", frequent: "Frecuente" };
const HASHTAG_LABELS = { minimal: "Mínimos", balanced: "Balanceados", many: "Muchos" };

export function SectionBrandVoice({ form }: Props) {
  const v = form.watch("brand_voice");
  const formats = v?.preferred_formats ?? [];
  type BV = OnboardingForm["brand_voice"];

  return (
    <div className="space-y-3">
      <div className="space-y-1"><Label className="text-xs">Tono</Label>
        <PillGroup options={TONES} value={v?.tone ?? ""}
          onChange={(x) => form.setValue("brand_voice.tone", x as BV["tone"])} cols={6} />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1"><Label className="text-xs">Emojis</Label>
          <PillGroup options={EMOJI_USAGE} labels={EMOJI_LABELS} value={v?.emoji_usage ?? ""}
            onChange={(x) => form.setValue("brand_voice.emoji_usage", x as BV["emoji_usage"])} cols={4} />
        </div>
        <div className="space-y-1"><Label className="text-xs">Hashtags</Label>
          <PillGroup options={HASHTAG_STRATEGY} labels={HASHTAG_LABELS} value={v?.hashtag_strategy ?? ""}
            onChange={(x) => form.setValue("brand_voice.hashtag_strategy", x as BV["hashtag_strategy"])} cols={3} />
        </div>
      </div>
      <div className="space-y-1"><Label className="text-xs">Keywords (separados por coma)</Label>
        <Input className="h-8" value={(v?.brand_voice_keywords ?? []).join(", ")}
          onChange={(e) => form.setValue("brand_voice.brand_voice_keywords", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} />
      </div>
      <div className="space-y-1"><Label className="text-xs">Temas a evitar</Label>
        <Textarea value={v?.avoided_topics ?? ""}
          onChange={(e) => form.setValue("brand_voice.avoided_topics", e.target.value)} rows={2} className="resize-none" />
      </div>
      <div className="space-y-1"><Label className="text-xs">Formatos preferidos</Label>
        <PillGroup options={CONTENT_FORMATS} value={formats} multi
          onChange={(x) => form.setValue("brand_voice.preferred_formats", x as BV["preferred_formats"])} cols={5} />
      </div>
    </div>
  );
}
