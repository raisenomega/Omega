// @vitest-environment jsdom
// Aislamiento del cache de Content Lab por negocio (fix /content-lab) · clave scopeada por businessId.
import { describe, it, expect, beforeEach } from "vitest";
import { loadPersistedResults, persistResults } from "@/lib/content-lab-persistence";
import type { ResultV2 } from "@/components/content/ResultCardV2";

const mk = (id: string, status: ResultV2["status"] = "completed"): ResultV2 =>
  ({ id, generated_text: id, content_type: "caption", status });
const KEY = (biz: string) => `omega_content_lab_results:${biz}`;
const LEGACY = "omega_content_lab_results";

beforeEach(() => localStorage.clear());

describe("content-lab-persistence · aislamiento por negocio", () => {
  it("1 · round-trip: persiste en A y lo carga de A", () => {
    persistResults("A", [mk("r1")]);
    expect(loadPersistedResults("A").map(r => r.id)).toEqual(["r1"]);
  });

  it("2 · aislamiento: lo de A NO se ve desde B", () => {
    persistResults("A", [mk("r1")]);
    expect(loadPersistedResults("B")).toEqual([]);
  });

  it("3 · null guard: load(null)=[] y persist(null,...) no escribe nada", () => {
    expect(loadPersistedResults(null)).toEqual([]);
    persistResults(null, [mk("r1")]);
    expect(loadPersistedResults("A")).toEqual([]);     // nada quedó escrito bajo ninguna clave
    expect(localStorage.length).toBe(0);
  });

  it("4 · cap MAX_PERSISTED=20: guarda los últimos 20", () => {
    persistResults("A", Array.from({ length: 25 }, (_, i) => mk(`r${i}`)));
    const ids = loadPersistedResults("A").map(r => r.id);
    expect(ids).toHaveLength(20);
    expect(ids[0]).toBe("r5");      // se descartan los 5 más viejos
    expect(ids[19]).toBe("r24");
  });

  it("5 · filtra status:'pending' (no persiste borradores en vuelo)", () => {
    persistResults("A", [mk("ok"), mk("vuela", "pending")]);
    expect(loadPersistedResults("A").map(r => r.id)).toEqual(["ok"]);
  });

  it("6 · A y B coexisten: DOS claves distintas en localStorage, sin colisión", () => {
    persistResults("A", [mk("ra")]);
    persistResults("B", [mk("rb")]);
    // Las dos claves scopeadas existen y son independientes:
    expect(localStorage.getItem(KEY("A"))).not.toBeNull();
    expect(localStorage.getItem(KEY("B"))).not.toBeNull();
    expect(localStorage.getItem(KEY("A"))).not.toBe(localStorage.getItem(KEY("B")));
    expect(loadPersistedResults("A").map(r => r.id)).toEqual(["ra"]);
    expect(loadPersistedResults("B").map(r => r.id)).toEqual(["rb"]);
  });

  it("7 · limpia el cache global legacy (sin sufijo) en el primer load con negocio", () => {
    localStorage.setItem(LEGACY, JSON.stringify([mk("viejo")]));
    loadPersistedResults("A");
    expect(localStorage.getItem(LEGACY)).toBeNull();   // borrado
    expect(loadPersistedResults("A")).toEqual([]);     // y NO se mezcla con el negocio
  });
});
