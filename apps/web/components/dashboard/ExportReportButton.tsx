"use client";

import type { StablecoinWithScore } from "@/types/risk";

function buildCsv(items: StablecoinWithScore[]): string {
  const header =
    "Symbol,Name,Chain,Rating,Score,Peg Price,Market Cap,Reserve,Issuer,Peg Stability,Regulatory,Sentiment,Updated";
  const rows = items.map((c) => {
    const s = c.risk_scores;
    return [
      c.symbol,
      `"${c.name}"`,
      c.chain,
      s?.rating ?? "",
      s?.score_numeric ?? "",
      c.peg_price ?? "",
      c.market_cap_usd ?? "",
      s?.reserve_subscore ?? "",
      s?.issuer_subscore ?? "",
      s?.peg_subscore ?? "",
      s?.regulatory_subscore ?? "",
      s?.sentiment_subscore ?? "",
      s?.updated_at ?? "",
    ].join(",");
  });
  return [header, ...rows].join("\n");
}

export function ExportReportButton({
  items,
}: {
  items: StablecoinWithScore[];
}) {
  function handleExport() {
    const csv = buildCsv(items);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `riskloom-report-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button className="dm-b dm-bs" onClick={handleExport}>
      Export Report
    </button>
  );
}
