import Link from "next/link";
import type { StablecoinWithScore } from "@/types/risk";
import { RatingPill, ratingBarFillClass, riskLevelForGrade } from "../ui/RatingPill";
import { formatPegPrice, formatMarketCap, pegPriceClass } from "@/lib/format";

const SCORE_TO_BAR_PCT: Record<string, number> = {
  AAA: 96, AA: 84, A: 75, BBB: 55, BB: 42, B: 30, CCC: 18, D: 5,
};

export function StablecoinTable({ items }: { items: StablecoinWithScore[] }) {
  return (
    <div>
      <div className="tbl-head">
        <div className="th">Stablecoin</div>
        <div className="th">StableScore&trade;</div>
        <div className="th">Peg Price</div>
        <div className="th">Market Cap</div>
        <div className="th">24h Change</div>
        <div className="th">Risk Level</div>
      </div>
      {items.map((coin) => {
        const rating = coin.risk_scores?.rating ?? "D";
        const level = riskLevelForGrade(rating);
        return (
          <Link href={`/stablecoins/${coin.symbol}`} className="tbl-row" key={coin.id}>
            <div>
              <div className="tc-name">{coin.name}</div>
              <div className="tc-sym">{coin.symbol}</div>
            </div>
            <div className="tc-rating">
              <div>
                <RatingPill grade={rating} />
                <div className="rat-bar">
                  <div
                    className={`rb-fill ${ratingBarFillClass(rating)}`}
                    style={{ width: `${SCORE_TO_BAR_PCT[rating] ?? 50}%` }}
                  />
                </div>
              </div>
            </div>
            <div className={`tc-peg ${pegPriceClass(coin.peg_price)}`}>
              {formatPegPrice(coin.peg_price)}
            </div>
            <div className="tc-cap">{formatMarketCap(coin.market_cap_usd)}</div>
            <div className="tc-chg" style={{ color: "var(--text2)" }}>--</div>
            <div className={`risk-ind ${level === "low" ? "low-r" : level === "medium" ? "mid-r" : "hi-r"}`}>
              <span className="ri-dot" />
              <span className="ri-lbl">{level === "low" ? "Low" : level === "medium" ? "Medium" : "Critical"}</span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
