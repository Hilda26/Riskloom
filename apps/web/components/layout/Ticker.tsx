import type { StablecoinWithScore } from "@/types/risk";
import { formatPegPrice, pegPriceClass } from "@/lib/format";

export function Ticker({ items }: { items: StablecoinWithScore[] }) {
  const doubled = [...items, ...items];
  return (
    <div className="ticker">
      <div className="ticker-label">&#11049; Live</div>
      <div className="ticker-track">
        {doubled.map((coin, i) => (
          <div className="ticker-item" key={`${coin.symbol}-${i}`}>
            <span className="ti-name">{coin.symbol}</span>
            <span className={`ti-score s-${(coin.risk_scores?.rating ?? "d").toLowerCase()}`}>
              {coin.risk_scores?.rating ?? "-"}
            </span>
            <span className={`ti-price ${pegPriceClass(coin.peg_price)}`}>
              {formatPegPrice(coin.peg_price)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
