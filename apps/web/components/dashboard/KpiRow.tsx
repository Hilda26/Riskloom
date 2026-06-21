import type { StablecoinWithScore } from "@/types/risk";
import { riskLevelForGrade } from "../ui/RatingPill";

export function KpiRow({ items }: { items: StablecoinWithScore[] }) {
  const tracked = items.length;
  const safe = items.filter(
    (i) => i.risk_scores && riskLevelForGrade(i.risk_scores.rating) === "low",
  ).length;
  const watchlist = items.filter(
    (i) => i.risk_scores && riskLevelForGrade(i.risk_scores.rating) === "medium",
  ).length;
  const critical = items.filter(
    (i) => i.risk_scores && riskLevelForGrade(i.risk_scores.rating) === "critical",
  ).length;

  const safePct = tracked > 0 ? ((safe / tracked) * 100).toFixed(1) : "0.0";

  return (
    <div className="krow">
      <div className="kpi k1">
        <div className="knum">{tracked}</div>
        <div className="klbl">Assets Tracked</div>
        <div className="ktrend kt-s">Live from Supabase</div>
      </div>
      <div className="kpi k2">
        <div className="knum">{safe}</div>
        <div className="klbl">AAA-A Rated</div>
        <div className="ktrend kt-s">{safePct}% safe</div>
      </div>
      <div className="kpi k3">
        <div className="knum">{watchlist}</div>
        <div className="klbl">&#9888; Watchlist</div>
        <div className="ktrend" style={{ color: "var(--warn)" }}>BB-B Rating</div>
      </div>
      <div className="kpi k4">
        <div className="knum">{critical}</div>
        <div className="klbl">&#x1f6a8; Critical</div>
        <div className="ktrend kt-d">CCC or D Rating</div>
      </div>
    </div>
  );
}
