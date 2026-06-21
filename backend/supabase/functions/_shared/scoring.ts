// Pure StableScore math, isolated from the Deno.serve handler so it can
// be unit tested directly (see backend/supabase/functions/_shared/scoring.test.ts).
// Mirrors the deterministic composite formula used as the starting point
// in intelligent-contracts/stablescore_oracle/contract.gpy::update_score.

export const GRADE_BOUNDARIES: [number, string][] = [
  [97, "AAA"],
  [90, "AA"],
  [80, "A"],
  [65, "BBB"],
  [50, "BB"],
  [35, "B"],
  [15, "CCC"],
  [0, "D"],
];

export function scoreToGrade(score: number): string {
  for (const [min, grade] of GRADE_BOUNDARIES) {
    if (score >= min) return grade;
  }
  return "D";
}

export interface Subscores {
  reserve: number;
  issuer: number;
  peg: number;
  regulatory: number;
  sentiment: number;
}

// Weighted composite across the five intelligence modules.
export function computeComposite(sub: Subscores): number {
  return (
    sub.reserve * 0.3 +
    sub.issuer * 0.2 +
    sub.peg * 0.25 +
    sub.regulatory * 0.15 +
    sub.sentiment * 0.1
  );
}
