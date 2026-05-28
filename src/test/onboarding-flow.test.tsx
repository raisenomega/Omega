// DEBT-099-v2 · wizard opcional · dashboard-first.
// shouldRedirectToOnboarding quedó como no-op (siempre false). El nudge usa
// isPlaceholderClient para decidir si invitar al wizard. Testeamos ambas.
import { describe, it, expect } from "vitest";
import {
  shouldRedirectToOnboarding,
  isPlaceholderClient,
} from "@/lib/onboarding-redirect";

const placeholder = { name: "Mi negocio", industry: null };
const completed = { name: "Real Biz", industry: "servicios" };
const partial = { name: "Mi negocio", industry: "servicios" };
const renamed = { name: "Real Biz", industry: null };

const base = {
  client: placeholder,
  isOwner: false,
  isSuperadmin: false,
  loading: false,
  currentPath: "/dashboard",
};

describe("shouldRedirectToOnboarding · DEBT-099-v2 (no-op)", () => {
  it("siempre false aun con placeholder · el wizard es opcional", () => {
    expect(shouldRedirectToOnboarding(base)).toBe(false);
  });
  it("siempre false aun en /onboarding mismo", () => {
    expect(shouldRedirectToOnboarding({ ...base, currentPath: "/onboarding" })).toBe(false);
  });
  it("siempre false con client null", () => {
    expect(shouldRedirectToOnboarding({ ...base, client: null })).toBe(false);
  });
});

describe("isPlaceholderClient · DEBT-099-v2 (decide visibilidad del nudge)", () => {
  it("placeholder (name='Mi negocio' + industry null) → true", () => {
    expect(isPlaceholderClient(placeholder)).toBe(true);
  });
  it("completed (name custom + industry set) → false", () => {
    expect(isPlaceholderClient(completed)).toBe(false);
  });
  it("partial (name='Mi negocio' + industry set) → false (user empezó)", () => {
    expect(isPlaceholderClient(partial)).toBe(false);
  });
  it("renamed (name custom + industry null) → false (user empezó)", () => {
    expect(isPlaceholderClient(renamed)).toBe(false);
  });
  it("client null → false (sin datos no se nudgea)", () => {
    expect(isPlaceholderClient(null)).toBe(false);
  });
});
