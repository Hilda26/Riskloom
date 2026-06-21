// Unit tests for the pure StableScore math. Run with: deno test backend/supabase/functions/_shared/scoring.test.ts
import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";
import { computeComposite, scoreToGrade } from "./scoring.ts";

Deno.test("computeComposite weights reserve heaviest, then peg, then issuer", () => {
  const allHundred = computeComposite({
    reserve: 100,
    issuer: 100,
    peg: 100,
    regulatory: 100,
    sentiment: 100,
  });
  assertEquals(allHundred, 100);

  const onlyReserve = computeComposite({
    reserve: 100,
    issuer: 0,
    peg: 0,
    regulatory: 0,
    sentiment: 0,
  });
  assertEquals(onlyReserve, 30);

  const onlyPeg = computeComposite({
    reserve: 0,
    issuer: 0,
    peg: 100,
    regulatory: 0,
    sentiment: 0,
  });
  assertEquals(onlyPeg, 25);
});

Deno.test("scoreToGrade boundaries match the documented StableScore bands", () => {
  assertEquals(scoreToGrade(100), "AAA");
  assertEquals(scoreToGrade(97), "AAA");
  assertEquals(scoreToGrade(96.9), "AA");
  assertEquals(scoreToGrade(90), "AA");
  assertEquals(scoreToGrade(80), "A");
  assertEquals(scoreToGrade(65), "BBB");
  assertEquals(scoreToGrade(50), "BB");
  assertEquals(scoreToGrade(35), "B");
  assertEquals(scoreToGrade(15), "CCC");
  assertEquals(scoreToGrade(14.9), "D");
  assertEquals(scoreToGrade(0), "D");
});

Deno.test("scoreToGrade never throws for out-of-range input", () => {
  assertEquals(scoreToGrade(-50), "D");
  assertEquals(scoreToGrade(1000), "AAA");
});

Deno.test("USDC seed subscores produce AAA, matching seed_stablecoins.sql", () => {
  const score = computeComposite({
    reserve: 99,
    issuer: 97,
    peg: 100,
    regulatory: 97,
    sentiment: 96,
  });
  assertEquals(Math.round(score * 100) / 100, 98.25);
  assertEquals(scoreToGrade(score), "AAA");
});

Deno.test("MIM seed subscores produce CCC, matching seed_stablecoins.sql", () => {
  const score = computeComposite({
    reserve: 12,
    issuer: 15,
    peg: 20,
    regulatory: 10,
    sentiment: 25,
  });
  assertEquals(scoreToGrade(score), "CCC");
});

// Every row in backend/supabase/seed/seed_stablecoins.sql, asserted
// against the live formula so the seed data can never silently drift
// from what compute-stablescore would itself produce from the same
// subscores - this caught a real mismatch (USDC/USDT/USDP/GUSD) before
// the seed file ever reached a database.
Deno.test("every seed_stablecoins.sql row is internally consistent with the scoring formula", () => {
  const seedRows: Array<{
    symbol: string;
    rating: string;
    score: number;
    reserve: number;
    issuer: number;
    peg: number;
    regulatory: number;
    sentiment: number;
  }> = [
    { symbol: "USDC", rating: "AAA", score: 98.25, reserve: 99, issuer: 97, peg: 100, regulatory: 97, sentiment: 96 },
    { symbol: "USDT", rating: "AA", score: 91.2, reserve: 90, issuer: 90, peg: 97, regulatory: 85, sentiment: 92 },
    { symbol: "DAI", rating: "A", score: 82.3, reserve: 78, issuer: 85, peg: 88, regulatory: 80, sentiment: 79 },
    { symbol: "FRAX", rating: "BBB", score: 66.55, reserve: 60, issuer: 70, peg: 72, regulatory: 65, sentiment: 68 },
    { symbol: "TUSD", rating: "BB", score: 55.55, reserve: 50, issuer: 58, peg: 60, regulatory: 55, sentiment: 57 },
    { symbol: "BUSD", rating: "B", score: 38.05, reserve: 35, issuer: 38, peg: 45, regulatory: 30, sentiment: 42 },
    { symbol: "USDP", rating: "AA", score: 91.5, reserve: 92, issuer: 92, peg: 94, regulatory: 88, sentiment: 88 },
    { symbol: "GUSD", rating: "A", score: 82.4, reserve: 80, issuer: 84, peg: 86, regulatory: 80, sentiment: 81 },
    { symbol: "LUSD", rating: "BBB", score: 65.5, reserve: 62, issuer: 66, peg: 70, regulatory: 64, sentiment: 66 },
    { symbol: "MIM", rating: "CCC", score: 15.6, reserve: 12, issuer: 15, peg: 20, regulatory: 10, sentiment: 25 },
  ];

  for (const row of seedRows) {
    const computed = computeComposite(row);
    assertEquals(
      Math.round(computed * 100) / 100,
      row.score,
      `${row.symbol}: seed score_numeric (${row.score}) does not match formula output (${computed})`,
    );
    assertEquals(
      scoreToGrade(computed),
      row.rating,
      `${row.symbol}: seed rating (${row.rating}) does not match the grade the formula derives (${scoreToGrade(computed)})`,
    );
  }
});
