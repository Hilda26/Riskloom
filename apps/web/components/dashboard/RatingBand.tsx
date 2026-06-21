import type { StableScoreGrade } from "@stableshield/shared-types";

const GRADES: { grade: StableScoreGrade; label: string; slot: string; cls: string }[] = [
  { grade: "AAA", label: "Extremely Safe", slot: "rs-aaa", cls: "c-aaa" },
  { grade: "AA", label: "Very Safe", slot: "rs-aa", cls: "c-aa" },
  { grade: "A", label: "Safe", slot: "rs-a", cls: "c-a" },
  { grade: "BBB", label: "Moderate", slot: "rs-bbb", cls: "c-bbb" },
  { grade: "BB", label: "Elevated", slot: "rs-bb", cls: "c-bb" },
  { grade: "B", label: "High Risk", slot: "rs-b", cls: "c-b" },
  { grade: "CCC", label: "Severe", slot: "rs-ccc", cls: "c-ccc" },
  { grade: "D", label: "Critical", slot: "rs-d", cls: "c-d" },
];

export function RatingBand({ counts }: { counts: Record<StableScoreGrade, number> }) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="sb-inner reveal">
      <div className="sb-top">
        <div>
          <div className="sb-title">StableScore&trade; Rating System</div>
          <div className="sb-sub">Continuous AI-powered risk ratings - updated every 60 seconds</div>
        </div>
        <div className="sb-live">
          <span className="sb-live-dot" />
          {total} stablecoins tracked
        </div>
      </div>
      <div className="ratings-row">
        {GRADES.map((g) => (
          <div className={`rating-slot ${g.slot}`} key={g.grade}>
            <span className={`rs-grade ${g.cls}`}>{g.grade}</span>
            <span className={`rs-label ${g.cls}`} style={{ opacity: 0.7 }}>{g.label}</span>
            <span className={`rs-count ${g.cls}`}>{counts[g.grade] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
