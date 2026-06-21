import type { StableScoreGrade } from "@stableshield/shared-types";

const GRADE_CLASS: Record<StableScoreGrade, string> = {
  AAA: "s-aaa",
  AA: "s-aa",
  A: "s-a",
  BBB: "s-bbb",
  BB: "s-bb",
  B: "s-b",
  CCC: "s-ccc",
  D: "s-d",
};

export function RatingPill({ grade }: { grade: StableScoreGrade }) {
  return <span className={`rat-pill ${GRADE_CLASS[grade]}`}>{grade}</span>;
}

export function riskLevelForGrade(
  grade: StableScoreGrade,
): "low" | "medium" | "critical" {
  if (["AAA", "AA", "A"].includes(grade)) return "low";
  if (["BBB", "BB"].includes(grade)) return "medium";
  return "critical";
}

export function ratingBarFillClass(grade: StableScoreGrade): string {
  const level = riskLevelForGrade(grade);
  if (level === "low") return "rb-safe";
  if (level === "medium") return "rb-warn";
  return "rb-danger";
}
