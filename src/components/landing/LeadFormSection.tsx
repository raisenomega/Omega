import { useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { Send, CheckCircle } from "lucide-react";
import { useLandingLang } from "@/landing/i18n/LandingLangContext";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { useSubmitLead } from "@/hooks/useSubmitLead";

// Sección de captura de leads · réplica visual del molde adaptada a los campos OMEGA (name/email/
// phone/message) + 2 pills de audience (preseleccionable por ?audience=). Escribe vía POST backend
// (la RLS de leads no permite anon-insert). P1: success sólo tras 2xx · error honesto si falla.
type Audience = "pyme" | "reseller";
const INPUT =
  "flex w-full rounded-md border border-input bg-secondary/50 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary";

export function LeadFormSection() {
  const { t } = useLandingLang();
  const { ref, isVisible } = useScrollReveal();
  const [params] = useSearchParams();
  const submit = useSubmitLead();
  const c = t.leadForm;
  const [audience, setAudience] = useState<Audience>(params.get("audience") === "reseller" ? "reseller" : "pyme");
  const [form, setForm] = useState({ name: "", email: "", phone: "", message: "", website: "" });
  const set = (k: keyof typeof form, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit.mutate({ name: form.name, email: form.email, phone: form.phone, message: form.message, website: form.website, audience });
  };

  if (submit.isSuccess) {
    return (
      <section id="lead-form" className="px-6 py-16 md:py-20">
        <div className="mx-auto flex max-w-2xl flex-col items-center gap-4 rounded-lg border border-primary/30 bg-card p-12 text-center">
          <CheckCircle size={48} className="text-primary" />
          <p className="text-lg font-medium text-foreground">{c.success}</p>
        </div>
      </section>
    );
  }

  return (
    <section
      id="lead-form"
      ref={ref}
      className={`px-6 py-16 transition-all duration-700 md:py-20 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
    >
      <div className="mx-auto max-w-2xl">
        <div className="mb-10 text-center">
          <h2 className="mb-4 font-display text-3xl font-bold tracking-tight text-foreground md:text-4xl">{c.title}</h2>
          <p className="text-muted-foreground">{c.subtitle}</p>
        </div>

        <div className="mb-6 flex gap-3">
          {(["pyme", "reseller"] as Audience[]).map((a) => (
            <button
              key={a}
              type="button"
              onClick={() => setAudience(a)}
              className={`flex-1 rounded-full border px-4 py-2 text-sm font-medium transition-colors ${audience === a ? "border-primary bg-primary/10 text-primary" : "border-input text-muted-foreground hover:text-foreground"}`}
            >
              {c[a]}
            </button>
          ))}
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <input className={INPUT} placeholder={c.name} value={form.name} onChange={(e) => set("name", e.target.value)} required minLength={2} />
          <input className={INPUT} type="email" placeholder={c.email} value={form.email} onChange={(e) => set("email", e.target.value)} required />
          <input className={INPUT} placeholder={c.phone} value={form.phone} onChange={(e) => set("phone", e.target.value)} />
          <textarea className={`${INPUT} resize-none`} rows={4} placeholder={c.message} value={form.message} onChange={(e) => set("message", e.target.value)} />
          <input type="text" tabIndex={-1} autoComplete="off" aria-hidden className="hidden" value={form.website} onChange={(e) => set("website", e.target.value)} />
          {submit.isError && <p className="text-sm text-destructive">{c.error}</p>}
          <button
            type="submit"
            disabled={submit.isPending}
            className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-8 py-3 font-display text-sm font-semibold text-primary-foreground transition-transform hover:scale-[1.02] disabled:opacity-50"
          >
            <Send size={16} /> {submit.isPending ? c.sending : c.cta}
          </button>
          <p className="text-center text-xs text-muted-foreground">{c.consent}</p>
        </form>
      </div>
    </section>
  );
}
