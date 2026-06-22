import { describe, it, expect } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { CONNECTABLE_PLATFORMS } from "@/lib/social-platforms-tab";

/** GUARDIA DE SINCRONÍA (no solo docstring): ata la fuente única del front al CHECK de la DB.
 * El docstring le pide al humano no desincronizar; este test se lo IMPONE a la máquina. Si
 * alguien suma una red a CONNECTABLE_PLATFORMS sin tocar el CHECK (o agrega al CHECK sin tocar
 * la constante), las 3 capas se separan y este test FALLA. Mismo blindaje que el assert que
 * impide reintroducir Posts en analytics. */
describe("social-platforms-tab ↔ CHECK de social_accounts.platform (migr 00071)", () => {
  const MIGRATIONS_DIR = join(process.cwd(), "supabase", "migrations");

  function checkPlatformsFromMigration(): string[] {
    const file = readdirSync(MIGRATIONS_DIR).find((f) => f.startsWith("00071"));
    expect(file, "migración 00071 no encontrada").toBeTruthy();
    const sql = readFileSync(join(MIGRATIONS_DIR, file as string), "utf-8");
    // ADD CONSTRAINT ... CHECK (platform IN ('a', 'b', ...)) → extrae los literales citados.
    const m = sql.match(/CHECK\s*\(\s*platform\s+IN\s*\(([^)]+)\)/i);
    expect(m, "no se halló CHECK (platform IN (...)) en la migración 00071").toBeTruthy();
    return [...(m as RegExpMatchArray)[1].matchAll(/'([^']+)'/g)].map((x) => x[1]);
  }

  it("el set del CHECK 00071 == CONNECTABLE_PLATFORMS (las 3 capas no divergen)", () => {
    const fromCheck = checkPlatformsFromMigration().sort();
    const fromConst = CONNECTABLE_PLATFORMS.map((p) => p.value).sort();
    expect(fromCheck).toEqual(fromConst);
  });

  it("el CHECK 00071 incluye 'reddit' (la red que esta migración habilita)", () => {
    expect(checkPlatformsFromMigration()).toContain("reddit");
  });
});
