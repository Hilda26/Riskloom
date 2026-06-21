export const STABLE_SCORE_GRADES = [
  "AAA",
  "AA",
  "A",
  "BBB",
  "BB",
  "B",
  "CCC",
  "D",
] as const;

export type StableScoreGrade = (typeof STABLE_SCORE_GRADES)[number];
