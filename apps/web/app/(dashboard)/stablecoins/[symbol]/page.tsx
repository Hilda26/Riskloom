import { createClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import { RatingPill } from "@/components/ui/RatingPill";
import { LiveContractPanel } from "@/components/oracle/LiveContractPanel";
import { formatPegPrice, formatMarketCap } from "@/lib/format";
import { fetchLiveMarketData } from "@/lib/marketdata";

export const revalidate = 0;

export default async function StablecoinDetailPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = await params;
  const supabase = await createClient();

  const { data: coin } = await supabase
    .from("stablecoins")
    .select("*, risk_scores(*)")
    .eq("symbol", symbol.toUpperCase())
    .maybeSingle();

  if (!coin) notFound();

  // Overlay live peg price / market cap from CoinGecko over the seed values.
  const live = await fetchLiveMarketData();
  const liveEntry = live[coin.symbol];
  if (liveEntry) {
    coin.peg_price = liveEntry.peg_price;
    coin.market_cap_usd = liveEntry.market_cap_usd ?? coin.market_cap_usd;
  }

  const { data: history } = await supabase
    .from("risk_score_history")
    .select("*")
    .eq("stablecoin_id", coin.id)
    .order("recorded_at", { ascending: false })
    .limit(10);

  const score = coin.risk_scores;

  return (
    <>
      <div className="dm-h">
        <div>
          <div className="dm-title">{coin.name} ({coin.symbol})</div>
          <div className="dm-sub">{coin.chain} - peg {formatPegPrice(coin.peg_price)} - cap {formatMarketCap(coin.market_cap_usd)}</div>
        </div>
        {score && <RatingPill grade={score.rating} />}
      </div>

      {score && (
        <div className="krow">
          <div className="kpi k1"><div className="knum">{score.reserve_subscore ?? "-"}</div><div className="klbl">Reserve Health</div></div>
          <div className="kpi k2"><div className="knum">{score.issuer_subscore ?? "-"}</div><div className="klbl">Issuer Intelligence</div></div>
          <div className="kpi k3"><div className="knum">{score.peg_subscore ?? "-"}</div><div className="klbl">Peg Stability</div></div>
          <div className="kpi k4"><div className="knum">{score.regulatory_subscore ?? "-"}</div><div className="klbl">Regulatory Risk</div></div>
        </div>
      )}

      <div className="oracle-lbl" style={{ marginTop: "2rem" }}>Score History</div>
      {(history ?? []).map((h) => (
        <div className="tbl-row" key={h.id} style={{ gridTemplateColumns: "1fr 1fr 2fr", cursor: "default" }}>
          <div><RatingPill grade={h.rating} /></div>
          <div className="tc-cap">{h.score_numeric}</div>
          <div className="tc-sym">{new Date(h.recorded_at).toLocaleString()} {h.reason_summary ? `- ${h.reason_summary}` : ""}</div>
        </div>
      ))}

      <div className="oracle-wrap" style={{ marginTop: "2rem" }}>
        <div className="oracle-grid" style={{ gridTemplateColumns: "1fr" }}>
          <LiveContractPanel symbol={coin.symbol} />
        </div>
      </div>
    </>
  );
}
