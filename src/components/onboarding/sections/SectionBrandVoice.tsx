import type { UseFormReturn } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { TONES, EMOJI_USAGE, HASHTAG_STRATEGY, CONTENT_FORMATS } from "@/lib/onboarding-constants";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Props { form: UseFormReturn<OnboardingForm> }

export function SectionBrandVoice({ form }: Props) {
  const v = form.watch("brand_voice");
  const formats = v?.preferred_formats ?? [];
  const toggleFormat = (f: typeof CONTENT_FORMATS[number]) => {
    const next = formats.includes(f) ? formats.filter((x) => x !== f) : [...formats, f];
    form.setValue("brand_voice.preferred_formats", next);
  };
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <div className="space-y-1"><Label className="text-sm">Tono</Label>
          <Select value={v?.tone ?? ""} onValueChange={(x) => form.setValue("brand_voice.tone", x as OnboardingForm["brand_voice"]["tone"])}>
            <SelectTrigger className="h-9"><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{TONES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
          </Select></div>
        <div className="space-y-1"><Label className="text-sm">Emojis</Label>
          <Select value={v?.emoji_usage ?? ""} onValueChange={(x) => form.setValue("brand_voice.emoji_usage", x as OnboardingForm["brand_voice"]["emoji_usage"])}>
            <SelectTrigger className="h-9"><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{EMOJI_USAGE.map((e) => <SelectItem key={e} value={e}>{e}</SelectItem>)}</SelectContent>
          </Select></div>
        <div className="space-y-1"><Label className="text-sm">Hashtags</Label>
          <Select value={v?.hashtag_strategy ?? ""} onValueChange={(x) => form.setValue("brand_voice.hashtag_strategy", x as OnboardingForm["brand_voice"]["hashtag_strategy"])}>
            <SelectTrigger className="h-9"><SelectValue placeholder="—" /></SelectTrigger>
            <SelectContent>{HASHTAG_STRATEGY.map((h) => <SelectItem key={h} value={h}>{h}</SelectItem>)}</SelectContent>
          </Select></div>
      </div>
      <div className="space-y-1"><Label className="text-sm">Keywords (separados por coma)</Label>
        <Input className="h-9" value={(v?.brand_voice_keywords ?? []).join(", ")} onChange={(e) => form.setValue("brand_voice.brand_voice_keywords", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} /></div>
      <div className="space-y-1"><Label className="text-sm">Temas a evitar</Label>
        <Textarea value={v?.avoided_topics ?? ""} onChange={(e) => form.setValue("brand_voice.avoided_topics", e.target.value)} rows={2} /></div>
      <div className="space-y-2"><Label className="text-sm">Formatos preferidos</Label>
        <div className="flex flex-wrap gap-2">{CONTENT_FORMATS.map((f) => (
          <label key={f} className="flex items-center gap-1 text-sm cursor-pointer">
            <Checkbox checked={formats.includes(f)} onCheckedChange={() => toggleFormat(f)} />{f}
          </label>))}</div></div>
    </div>
  );
}
