// DEBT-099 · self-service onboarding · test de la función pura de decisión de redirect.
// Mockear React Router + react-query es ruido; extraemos la lógica a una función pura
// (shouldRedirectToOnboarding) y testeamos solo eso. El hook que la consume es trivial.
import { describe, it, expect } from "vitest";
import { shouldRedirectToOnboarding } from "@/lib/onboarding-redirect";

const placeholder = { name: "Mi negocio", industry: null };
const completed = { name: "Real Biz", industry: "servicios" };
const partial = { name: "Mi negocio", industry: "servicios" };  // user completó industry pero no nombre
const renamed = { name: "Real Biz", industry: null };  // user cambió nombre pero no industry

const base = {
  client: placeholder,
  isOwner: false,
  isSuperadmin: false,
  loading: false,
  currentPath: "/dashboard",
};

describe("shouldRedirectToOnboarding · DEBT-099", () => {
  it("placeholder en /dashboard → redirect TRUE", () => {
    expect(shouldRedirectToOnboarding(base)).toBe(true);
  });
  it("loading=true → esperar · no redirect", () => {
    expect(shouldRedirectToOnboarding({ ...base, loading: true })).toBe(false);
  });
  it("ya en /onboarding → no re-redirect (evita loop)", () => {
    expect(shouldRedirectToOnboarding({ ...base, currentPath: "/onboarding" })).toBe(false);
  });
  it("isOwner=true (reseller) → bypass aunque haya placeholder", () => {
    expect(shouldRedirectToOnboarding({ ...base, isOwner: true })).toBe(false);
  });
  it("isSuperadmin=true (super_owner) → bypass aunque haya placeholder", () => {
    expect(shouldRedirectToOnboarding({ ...base, isSuperadmin: true })).toBe(false);
  });
  it("client completo (name + industry) → no redirect", () => {
    expect(shouldRedirectToOnboarding({ ...base, client: completed })).toBe(false);
  });
  it("client parcial (industry set · name 'Mi negocio') → no redirect (user empezó)", () => {
    expect(shouldRedirectToOnboarding({ ...base, client: partial })).toBe(false);
  });
  it("client renombrado (name custom · industry null) → no redirect (user empezó)", () => {
    expect(shouldRedirectToOnboarding({ ...base, client: renamed })).toBe(false);
  });
  it("client null → no redirect (safe default · trigger 00006 lo crea siempre)", () => {
    expect(shouldRedirectToOnboarding({ ...base, client: null })).toBe(false);
  });
});
