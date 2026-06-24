// Live market data for the tracked stablecoins, pulled from CoinGecko's
// free public API (no key required). This replaces the static seed peg
// price / market cap with real, current values so the dashboard reflects
// live conditions - including real depeg events. If CoinGecko is
// unreachable or rate-limited, callers fall back to the Supabase seed
// values, so the app degrades gracefully and never shows nothing.

// Our internal symbol -> CoinGecko coin id.
const COINGECKO_IDS: Record<string, string> = {
  USDC: "usd-coin",
  USDT: "tether",
  DAI: "dai",
  FRAX: "frax",
  TUSD: "true-usd",
  BUSD: "binance-usd",
  USDP: "paxos-standard",
  GUSD: "gemini-dollar",
  LUSD: "liquity-usd",
  MIM: "magic-internet-money",
};

export interface LiveMarketEntry {
  peg_price: number;
  market_cap_usd: number | null;
}

export type LiveMarketMap = Record<string, LiveMarketEntry>;

// Returns a map keyed by our internal symbol. Empty map on any failure -
// callers should treat a missing symbol as "use the seed value".
export async function fetchLiveMarketData(): Promise<LiveMarketMap> {
  const ids = Object.values(COINGECKO_IDS).join(",");
  const url =
    `https://api.coingecko.com/api/v3/simple/price?ids=${ids}` +
    `&vs_currencies=usd&include_market_cap=true`;

  try {
    // Next.js caches this fetch for 60s across all requests/pages, which
    // keeps us comfortably inside CoinGecko's free rate limit no matter
    // how many people load the dashboard.
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) return {};
    const data = (await res.json()) as Record<
      string,
      { usd?: number; usd_market_cap?: number }
    >;

    const out: LiveMarketMap = {};
    for (const [symbol, id] of Object.entries(COINGECKO_IDS)) {
      const row = data[id];
      if (row && typeof row.usd === "number") {
        out[symbol] = {
          peg_price: row.usd,
          market_cap_usd:
            typeof row.usd_market_cap === "number" ? row.usd_market_cap : null,
        };
      }
    }
    return out;
  } catch {
    return {};
  }
}

// Overlays live peg price / market cap onto a list of rows that each have
// a `symbol`, falling back to whatever the row already had when live data
// for that symbol is unavailable.
export function applyLiveMarketData<
  T extends { symbol: string; peg_price: number; market_cap_usd: number | null },
>(rows: T[], live: LiveMarketMap): T[] {
  return rows.map((row) => {
    const entry = live[row.symbol];
    if (!entry) return row;
    return {
      ...row,
      peg_price: entry.peg_price,
      market_cap_usd: entry.market_cap_usd ?? row.market_cap_usd,
    };
  });
}
